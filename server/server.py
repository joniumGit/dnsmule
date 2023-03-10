from logging import INFO, StreamHandler
from pathlib import Path
from textwrap import dedent
from typing import Union, Dict, Any, Optional, List

from fastapi import FastAPI, Query, BackgroundTasks, Depends
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, validator, ValidationError, Extra

from dnsmule import DNSMule, RRType, __version__

app = FastAPI(
    default_response_class=Response,
    title='DNSMule Example Server',
    version=__version__,
    description=dedent(
        '''
        This is an example server for the DNSMule tool.
        The server allows easy evaluation of rules ad data gathering from domains.
        The current data storage is done in memory and no persistence is offered.
        '''
    ),
    openapi_tags=[
        {
            'name': 'Common',
            'description': 'API Methods for scanning and results.',
        },
        {
            'name': 'System',
            'description': 'API Methods for rules, plugins, and storage.'
        }
    ],
)
rules = Path(__file__).parent.parent / 'rules' / 'rules.yml'


@app.exception_handler(ValidationError)
async def handle(r, e):
    return await request_validation_exception_handler(r, e)


def get_mule() -> DNSMule:
    return app.state.mule


@app.on_event('startup')
def startup():
    from dnsmule.config import get_logger

    get_logger().addHandler(StreamHandler())
    get_logger().setLevel(INFO)

    mule = DNSMule(file=rules)
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

    @validator('record')
    def validate_record(cls, v):
        return RRType.from_any(v)

    class Config:
        schema_extra = {
            'example': {
                'type': 'dns.regex',
                'name': 'my-sample-rule',
                'record': 'A',
                'config': {
                    'pattern': r'^(?:\d+\.)+$',
                },
            },
        }


class RuleQuery(BaseModel):
    name: str
    record: Optional[Union[str, int]]

    @validator('record')
    def validate_record(cls, v):
        if v is not None:
            return RRType.from_any(v)


class Result(BaseModel):
    domain: str
    type: List[str]
    tags: List[str]
    data: Dict[str, Any]


class ResultsCollection(BaseModel):
    results: List[Result]


class PluginsCollection(BaseModel):
    plugins: List[str]

    class Config:
        schema_extra = {
            'example': {
                'plugins': [
                    'dnsmule_plugins.CertCheckPlugin',
                    'dnsmule_plugins.IPRangesPlugin',
                    'dnsmule_plugins.PTRScanPlugin',
                ],
            },
        }


class RulesCollection(BaseModel):
    __root__: Dict[str, List[str]]

    class Config:
        extra = Extra.allow
        schema_extra = {
            'example': {
                'A': [
                    'test_rule_1',
                    'test_rule_2',
                ],
                '65530': [
                    'test_rule_1',
                    'test_rule_x',
                ]
            }
        }


_DOMAIN_VALIDATION_EXAMPLE: Dict[str, Any] = {
    'description':
        'This error is returned only if the domain query is malformed.',
    'content': {
        'application/json': {
            'examples': {
                'error': {
                    'summary': 'Validation Error',
                    'value': {
                        'detail': [
                            {
                                'loc': [
                                    'query',
                                    'domain'
                                ],
                                'msg': 'string does not match regex "^(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z0-9-]+$"',
                                'type': 'value_error.str.regex',
                                'ctx': {
                                    'pattern': '^(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z0-9-]+$'
                                },
                            },
                        ],
                    },
                },
            },
        },
    },
}

_RECORD_VALIDATION_EXAMPLE: Dict[str, Any] = {
    'description':
        'This error is returned when an invalid value is given for the RRType of the rule.',
    'content': {
        'application/json': {
            'examples': {
                'record': {
                    'summary': 'Invalid RRType',
                    'value': {
                        'detail': [
                            {
                                'loc': [
                                    'record'
                                ],
                                'msg': 'invalid literal for int() with base 10: "EXAMPLE"',
                                'type': 'value_error',
                            },
                        ],
                    },
                },
            },
        },
    },
}


@app.post(
    '/scan',
    status_code=202,
    tags=['Common'],
    description='Queue a scan for a domain.',
    responses={
        202: {
            'description':
                'The requested domain was queued for processing and will appear in results later.',
        },
        422: _DOMAIN_VALIDATION_EXAMPLE,
        425: {
            'description':
                'Indicates the previous scan for this domain has not yet completed '
                'and a new one could not be started.',
        },
    },
)
async def scan_domain(tasks: BackgroundTasks, domain: str = domain_query(), mule: DNSMule = Depends(get_mule)):
    tasks.add_task(mule.run, domain)


@app.get(
    '/results',
    response_class=JSONResponse,
    status_code=200,
    tags=['Common'],
    response_model=Union[ResultsCollection, Result],
    description='Fetch all results on the server or query a single result for a domain.',
    responses={
        200: {
            'description':
                'Returns all results in server memory '
                'or a single result based the query parameter.',
            'content': {
                'application/json': {
                    'examples': {
                        'all': {
                            'summary': 'Get all results',
                            'value': {
                                'results': [
                                    {
                                        'domain': 'example.com',
                                        'type': [
                                            'A',
                                            'TXT',
                                        ],
                                        'data': {
                                            'sample': True,
                                        },
                                    },
                                ],
                            },
                        },
                        'single': {
                            'summary': 'Get a single result',
                            'description':
                                'This is the response when a query param is present.'
                                'A 404 is returned if the requested result is not found.',
                            'value': {
                                'domain': 'example.com',
                                'type': [
                                    'A',
                                    'TXT',
                                ],
                                'data': {
                                    'sample': True,
                                },
                            },
                        },
                    },
                },
            },
        },
        404: {
            'description':
                'A 404 is returned when results for a domain are queried '
                'and the domain is not found present in results.',
        },
        422: _DOMAIN_VALIDATION_EXAMPLE,
    },
)
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


@app.get(
    '/rules',
    response_class=JSONResponse,
    status_code=200,
    tags=['System'],
    response_model=RulesCollection,
    description='Returns all rules active in the DNSMule running on the server grouped by type.',
)
def get_rules(mule: DNSMule = Depends(get_mule)):
    return {
        str(RRType.from_any(record)): [
            rule.name
            for rule in collection
        ]
        for record, collection in mule.rules.items()
        if collection
    }


@app.post(
    '/rules',
    status_code=201,
    tags=['System'],
    description='Allows creating new rules during runtime.',
    responses={
        201: {
            'description':
                'The requested rule was successfully created',
        },
        409: {
            'description':
                'A rule with the same name and RRType already exists.',
        },
        400: {
            'description':
                'Something failed while creating the rule. '
                'These are raw errors from the rule constructors or init methods.',
            'content': {
                'application/json': {
                    'examples': {
                        'no-rtype': {
                            'summary': 'Missing rule type',
                            'value': {
                                'detail': [
                                    {
                                        'msg': 'TypeError("first argument must be string or compiled pattern")',
                                    },
                                ],
                            },
                        },
                    },
                },
            },
        },
        404: {
            'description':
                'Failed to find the requested rule type',
            'content': {
                'application/json': {
                    'examples': {
                        'no-rtype': {
                            'summary': 'Missing rule type',
                            'value': {
                                'detail': [
                                    {
                                        'msg': 'Failed to find rule type "[object Object]"'
                                    }
                                ]
                            },
                        },
                    },
                },
            },
        },
        422: _RECORD_VALIDATION_EXAMPLE,
    }
)
def create_rule(response: Response, definition: RuleDefinition, mule: DNSMule = Depends(get_mule)):
    if mule.rules.has_rule(definition.record, definition.name):
        response.status_code = 409
    else:
        try:
            definition.config['name'] = definition.name
            rule = mule.rules.create_rule(definition.type, definition.config)
            mule.rules.add_rule(definition.record, rule)
        except KeyError as e:

            return JSONResponse({
                'detail': [
                    {
                        'type': 'key_error',
                        'msg': f'Failed to find rule type {str(e)}',
                    },

                ],
            }, status_code=404)
        except Exception as e:
            import traceback
            tb = traceback.format_exc(None, True)
            return JSONResponse({
                'detail': [
                    {
                        'type': 'exception',
                        'msg': repr(e),
                    },
                    {
                        'type': 'traceback',
                        'msg': tb,
                    },
                ],
            }, status_code=400)


@app.delete(
    '/rules',
    status_code=204,
    tags=['System'],
    description=(
            'Allows deleting rules by name and record type. '
            'If a record type is not specified all rules matching the provided name are deleted.'
    ),
    responses={
        204: {
            'description':
                'The server successfully deleted the requested rule(s).',
        },
        404: {
            'description':
                'Any rules matching the deletion criteria were not found.',
        },
        422: _RECORD_VALIDATION_EXAMPLE,
    }
)
def delete_rule(query: RuleQuery = Depends(), mule: DNSMule = Depends(get_mule)):
    deleted = False
    for rtype, collection in mule.rules.items():
        if not query.record or rtype == query.record:
            to_remove = []
            for item in collection:
                if item.name == query.name:
                    to_remove.append(item)
            for item in to_remove:
                collection.remove(item)
            deleted = to_remove or deleted
    if not deleted:
        return Response(status_code=404)


@app.post(
    '/rescan',
    status_code=202,
    tags=['Common'],
    description='Re-Scans all previously submitted domains.',
    responses={
        202: {
            'description':
                'All previously scanned domains were queued for reprocessing.',
        },
        425: {
            'description':
                'Indicates the previous rescan has not yet completed and a new one could not be started.',
        },
    },
)
def rescan(tasks: BackgroundTasks, response: Response, mule: DNSMule = Depends(get_mule)):
    domains = mule.domains()
    response.headers['scan-count'] = str(len(domains))
    for domain in domains:
        tasks.add_task(mule.run, domain)


@app.get(
    '/plugins',
    status_code=200,
    response_class=JSONResponse,
    tags=['System'],
    response_model=PluginsCollection,
    description='Returns all plugins enabled in the DNSMule running on the server.',
)
def get_plugins(mule: DNSMule = Depends(get_mule)):
    return {
        'plugins': [
            *mule.plugins,
        ]
    }


if __name__ == '__main__':  # pragma: nocover
    import uvicorn

    uvicorn.run(
        'server:app',
        reload_dirs=str(Path(__file__).parent),
        reload=True,
    )
