import uvicorn
from models.main import Сustom 
from env import Env
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class CustomMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		response = await call_next(request)
		if response.status_code == 404:
			return RedirectResponse('/error_404')

		return response


app = FastAPI(docs_url=None, redoc_url=None)
app.add_middleware(CORSMiddleware, allow_headers=['*'], allow_methods=['*'], allow_origins=['*'])
app.add_middleware(CustomMiddleware)


env = Env()
env_data = env.data()


custom_model = Сustom(env_data)


@app.get('/error_404', name='error_404', description='Redirect to this page, if route not found.')
async def error_404():
	return HTMLResponse(content='<div style="width: 100%; text-align: center;"><h1>Page not found!</h1></div>', status_code=200)


@app.get('/invoke_ai', name='invoke_ai', description='Calling AI to answer a question.')
def invoke_ai(token: str = Query(...)):
	response_json = {'status': 'error', 'err_description': None, 'response': None}
	status_code = 500

	try:
		invoke_ai = custom_model.invoke_ai(token)
		status = invoke_ai['status']
		err_description = invoke_ai['err_description']
		response = invoke_ai['response']

		response_json['status'] = status
		response_json['err_description'] = err_description
		response_json['response'] = response

		status_code = 200

	except Exception as e:
		response_json['err_description'] = str(e)

	return JSONResponse(content=response_json, status_code=status_code)


if __name__ == '__main__':
	uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
	customClass = Сustom('How many planets are in the solar system?')
	invoke_ai = customClass.invoke_ai()
	print(invoke_ai)

