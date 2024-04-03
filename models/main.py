import boto3
import json
import jwt
from loguru import logger
from abc import ABC, abstractmethod


class Main(ABC):
	@abstractmethod
	def _generate_text(self):
		pass


class Performer(Main):
	def _generate_text(self, prompt):
		response_json = {'status': 'error', 'err_description': None, 'response': None}

		try:
			body = json.dumps({
				"inputText": prompt,
				"textGenerationConfig": {
					"maxTokenCount": 800,
					"stopSequences": [],
					"temperature": 0.5,
					"topP": 1
				}
			})

			invoke_model = self.bedrock.invoke_model(
				body=body, modelId=self.model_id, accept='application/json', contentType='application/json'
			)

			response_body = json.loads(invoke_model.get("body").read().decode())
			error = response_body.get("error")

			if error is not None:
				response_json['err_description'] = error
				return response_json

			response_json['status'] = 'success'
			outputText = response_body.get('results', [{}])[0].get('outputText', None)
			if outputText is not None:
				outputText = outputText.replace('\n', '')

			response_json['response'] = outputText

		except Exception as e:
			response_json['err_description'] = str(e)
	    
		return response_json


class Сustom(Performer):
	def __init__(self, env_data):
		aws_access_key_id = env_data.get('aws_access_key_id')
		aws_secret_access_key = env_data.get('aws_secret_access_key')

		self.jwt_secret_key = env_data.get('jwt_secret_key')
		self.bedrock = boto3.client(service_name='bedrock-runtime', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-east-1')
		self.model_id = 'amazon.titan-text-express-v1'

	def invoke_ai(self, token):
		response_json = {'status': 'error', 'err_description': None, 'response': None}

		try:
			data = jwt.decode(token, self.jwt_secret_key, algorithms=['HS256'])
			prompt = data.get('prompt')
			if prompt is None:
				response_json['err_description'] = 'Prompt not found!'
				return response_json

			generate_text = self._generate_text(prompt)
			status = generate_text['status']
			err_description = generate_text['err_description']
			response = generate_text['response']

			response_json['status'] = status
			response_json['err_description'] = err_description
			response_json['response'] = response

		except Exception as e:
			response_json['err_description'] = str(e)

		return response_json