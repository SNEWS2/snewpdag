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

histogram:
	python snewpdag/trials/Normal.py hist --expt Newt | \
          python -m snewpdag --jsonlines \
          snewpdag/data/test-dags-hist-config.json

trial:
	python snewpdag/trials/Simple.py Control -n 10 | \
          python -m snewpdag --jsonlines snewpdag/data/test-gen-config.py

trial2:
	python snewpdag/trials/Simple.py Control -n 10 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-liq-config.py

init:
	pip install -r requirements.txt

.PHONY: init run test histogram trial trial2 runtest
