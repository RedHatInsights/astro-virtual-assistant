# install and train the project
install:
	pipenv install --dev

train:
	pipenv run rasa train --domain data

finetune:
	pipenv run rasa train --domain data --finetune

# runs the assistant
run:
	pipenv run rasa run

run-actions:
	pipenv run rasa run actions --auto-reload

run-cli:
	pipenv run rasa shell

# validate and test changes
validate: 
	pipenv run rasa data validate --fail-on-warnings --domain data

test:
	pipenv run rasa test --fail-on-prediction-errors

test-identity:
	curl -X POST http://0.0.0.0:5005/api/virtual-assistant/talk -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiJhY2NvdW50MTIzIiwib3JnX2lkIjoib3JnMTIzIiwidHlwZSI6IlVzZXIiLCJ1c2VyIjp7ImlzX29yZ19hZG1pbiI6dHJ1ZSwgInVzZXJfaWQiOiIxMjM0NTY3ODkwIn0sImludGVybmFsIjp7Im9yZ19pZCI6Im9yZzEyMyJ9fX0=" -H "Content-Type: application/json" --data '{ "message": "Hi there!", "metadata": {} }'
