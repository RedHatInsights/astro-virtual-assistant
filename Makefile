train:
	pipenv run rasa train

run:
	pipenv run rasa run

run-actions:
	pipenv run rasa run actions --auto-reload

run-cli:
	pipenv run rasa shell

test-identity:
	curl -X POST http://0.0.0.0:5005/webhooks/identity/webhook -H "x-rh-identity: test" -H "Content-Type: application/json" --data '{ "sender": "test_user", "message": "Hi there!", "metadata": {} }'
