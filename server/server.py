from pathlib import Path
from threading import Lock
from typing import Union, Dict, Any

from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.definitions import Domain, Result, RRType
from dnsmule.rules import load_config

app = FastAPI(default_response_class=Response)
rules = load_config(Path(__file__).parent.parent / 'rules' / 'rules.yml')
results: Dict[Union[str, Domain], Result] = {}
backend = DNSPythonBackend(rules)

results_lock = Lock()
rules_lock = Lock()


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


async def scan_task(domain: str):
    async for result in backend.run_single(Domain(domain)):
        with results_lock:
            if result.domain in results:
                results[result.domain] += result
            else:
                results[result.domain] = result


@app.post('/scan', status_code=202)
async def scan_domain(tasks: BackgroundTasks, domain: str = domain_query()):
    tasks.add_task(scan_task, domain)


@app.get('/results', response_class=JSONResponse, status_code=200)
def get_domain(domain: str = domain_query(None)):
    if domain:
        if domain in results:
            return results[domain].to_json()
        else:
            return Response(status_code=404)
    else:
        return {
            'results': [
                result.to_json()
                for result in results.values()
            ]
        }


@app.get('/rules', response_class=JSONResponse, status_code=200)
def get_rules():
    return {
        RRType.to_text(record): [
            rule.name
            for rule in collection
        ]
        for record, collection in rules
    }


@app.post('/rules', status_code=201)
def create_rule(definition: RuleDefinition):
    with rules_lock:
        definition.config['name'] = definition.name
        definition.config['type'] = definition.type
        rule = rules.create_rule(definition.config)
        rules.add_rule(definition.record, rule)


@app.delete('/rules', status_code=204)
def delete_rule(record: str = Query(None), name: str = Query(...)):
    with rules_lock:
        for rtype, collection in rules:
            if not record or rtype == RRType.from_any(record):
                to_remove = []
                for item in collection:
                    if item.name == name:
                        to_remove.append(item)
                for item in to_remove:
                    collection.remove(item)


@app.post('/rescan', status_code=202)
def rescan(tasks: BackgroundTasks, response: Response):
    response.headers['scan-count'] = str(len(results))
    for domain in results.keys():
        tasks.add_task(scan_task, domain.name)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
