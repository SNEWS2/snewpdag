run: init
	echo python -m snewpdag # needs config and input JSON filenames

lightcurvesim:
	cd externals/lightcurve_match && make simulation
	cd externals/lightcurve_match/matching && make getdelay

test: lightcurvesim
	python -m unittest snewpdag.tests.test_basic_node
	python -m unittest snewpdag.tests.test_inputs
	python -m unittest snewpdag.tests.test_app
	python -m unittest snewpdag.tests.test_combinemaps
	python -m unittest snewpdag.tests.test_timedistdiff

runtest:
	python -m snewpdag \
          --input snewpdag/data/text-flux-input.json \
          snewpdag/data/text-flux-config.json

trial:
	python snewpdag/trials/Normal.py hist --expt Newt | \
          python -m snewpdag --jsonlines \
          snewpdag/data/test-dags-hist-config.json

init:
	pip install -r requirements.txt

.PHONY: init run test trial runtest
