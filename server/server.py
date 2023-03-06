from logging import INFO, StreamHandler
from pathlib import Path
from typing import Union, Dict, Any

from fastapi import FastAPI, Query, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from dnsmule import DNSMule, RRType

app = FastAPI(default_response_class=Response)


def get_mule() -> DNSMule:
    return app.state.mule


@app.on_event('startup')
def startup():
    from dnsmule.config import get_logger

    get_logger().addHandler(StreamHandler())
    get_logger().setLevel(INFO)

    mule = DNSMule(file=Path(__file__).parent.parent / 'rules' / 'rules.yml')

    try:
        from dnsmule.rules.utils import load_rules
        from dnsmule_plugins import certcheck, ipranges

        certcheck.plugin_certcheck(mule.rules, lambda ds: mule.store_domains(ds))
        ipranges.plugin_ipranges(mule.rules)

        load_rules([
            {
                'record': 'A',
                'type': 'ip.certs',
                'name': 'certcheck',
            },
            {
                'record': 'A',
                'type': 'ip.ranges',
                'name': 'ipranges',
                'providers': [
                    'amazon',
                    'microsoft',
                    'google',
                ]
            },
        ], rules=mule.rules)

        if mule.backend == 'DNSPythonBackend':
            from dnsmule_plugins import ptrscan

            ptrscan.plugin_ptr_scan(mule.rules, mule.get_backend())
            load_rules([
                {
                    'record': 'A',
                    'type': 'ip.ptr',
                    'name': 'ptrscan',
                },
            ], rules=mule.rules)
    except ImportError:
        pass

    app.state.mule = mule


def domain_query(default=...):
    return Query(
        default,
        # language=pythonregexp
        regex=r'^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+$',
        max_length=63,
    )


class RuleDefinition(BaseModel):
    type: str
    record: Union[str, int]
    name: str
    config: Dict[str, Any]


@app.post('/scan', status_code=202)
async def scan_domain(tasks: BackgroundTasks, domain: str = domain_query(), mule: DNSMule = Depends(get_mule)):
    tasks.add_task(mule.run, domain)


@app.get('/results', response_class=JSONResponse, status_code=200)
def get_domain(domain: str = domain_query(None), mule: DNSMule = Depends(get_mule)):
    if domain:
        if domain in mule:
            return mule[domain].to_json()
        else:
            return Response(status_code=404)
    else:
        return {
            'results': [
                result.to_json()
                for result in mule.values()
            ]
        }


@app.get('/rules', response_class=JSONResponse, status_code=200)
def get_rules(mule: DNSMule = Depends(get_mule)):
    return {
        RRType.to_text(record): [
            rule.name
            for rule in collection
        ]
        for record, collection in mule.rules.items()
    }


@app.post('/rules', status_code=201)
def create_rule(definition: RuleDefinition, mule: DNSMule = Depends(get_mule)):
    definition.config['name'] = definition.name
    definition.config['type'] = definition.type

    rule = mule.rules.create_rule(definition.config)
    mule.rules.add_rule(definition.record, rule)


@app.delete('/rules', status_code=204)
def delete_rule(record: Union[int, str] = Query(None), name: str = Query(...), mule: DNSMule = Depends(get_mule)):
    for rtype, collection in mule.rules:
        if not record or rtype == RRType.from_any(record):
            to_remove = []
            for item in collection:
                if item.name == name:
                    to_remove.append(item)
            for item in to_remove:
                collection.remove(item)


@app.post('/rescan', status_code=202)
def rescan(tasks: BackgroundTasks, response: Response, mule: DNSMule = Depends(get_mule)):
    domains = mule.domains()
    response.headers['scan-count'] = str(len(domains))
    for domain in domains:
        tasks.add_task(mule.run, domain)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'server:app',
        reload_dirs=str(Path(__file__).parent),
        reload=True,
    )
