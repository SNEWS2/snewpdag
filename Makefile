
test:
	python -m unittest snewpdag.tests.test_shape
	python -m unittest snewpdag.tests.test_basic_node
	python -m unittest snewpdag.tests.test_inputs
	python -m unittest snewpdag.tests.test_app
	python -m unittest snewpdag.tests.test_combinemaps
	python -m unittest snewpdag.tests.test_shape

init:
	pip install -r requirements.txt

run:
	python -m snewpdag # needs config and input JSON filenames

.PHONY: init run test

