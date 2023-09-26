run: init
	echo python -m snewpdag # needs config and input JSON filenames

lightcurvesim:
	cd externals/lightcurve_match && make simulation
	cd externals/lightcurve_match/matching && make getdelay

standalone_unittests:
	python -m unittest snewpdag.tests.test_basic_node
	python -m unittest snewpdag.tests.test_app
	python -m unittest snewpdag.tests.test_inputs
	python -m unittest snewpdag.tests.test_combinemaps
	python -m unittest snewpdag.tests.test_copy
	python -m unittest snewpdag.tests.test_lib
	python -m unittest snewpdag.tests.test_values

test: standalone_unittests lightcurvesim
	python -m unittest snewpdag.tests.test_timedistdiff

runtest:
	python -m snewpdag \
          --input snewpdag/data/test-flux-input.json \
          snewpdag/data/test-flux-config.json

histogram:
	python snewpdag/trials/Normal.py hist --expt Newt | \
          python -m snewpdag --jsonlines \
          snewpdag/data/test-dags-hist-config.json

Hop_stream:
	python -m snewpdag --stream STREAM --log INFO snewpdag/data/test-hop-stream-config.py 
        	  
trial:
	python snewpdag/trials/Simple.py Control -n 10 | \
          python -m snewpdag --jsonlines snewpdag/data/test-gen-config.py

trial2:
	python snewpdag/trials/Simple.py Control -n 10 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-liq-config.py

pickle_output:
	python snewpdag/trials/Simple.py Control -n 10 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-pickle-out.py

pickle_input:
	python snewpdag/trials/Simple.py Control -n 1 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-pickle-in.py

diffpointing:
	python snewpdag/trials/Simple.py Control -n 1 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-diff.csv

diffpointing_smear:
	#python snewpdag/trials/Simple.py Control -n 1 | \
        #  python -m snewpdag --jsonlines snewpdag/data/test-diff-low-res.csv
	#python snewpdag/trials/Simple.py Control -n 10000 | \
        #  python -m snewpdag --jsonlines snewpdag/data/test-diff-smear.csv
	python snewpdag/trials/Simple.py Control -n 100 | \
          python -m snewpdag --jsonlines snewpdag/data/test-pointing.csv

diffpointing_weighted:
	python snewpdag/trials/Simple.py Control -n 100 | \
          python -m snewpdag --jsonlines snewpdag/data/test-pointing-weighted.csv

diffpointing_bias:
	python snewpdag/trials/Simple.py Control -n1 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-bias.csv 

#evalmap_weighted:
#	python snewpdag/trials/Simple.py Control -n1000 | \
#	  python -m snewpdag --jsonlines snewpdag/data/test-eq-weighted.csv

distcalc_trial:
	python snewpdag/trials/Simple.py Control -n 1000 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-distcalc-single-config.csv

distcalc_err_trial:
	python snewpdag/trials/Simple.py Control -n 5000 | \
          python -m snewpdag --log INFO --jsonlines snewpdag/data/test-distcalc-err-config.csv

fd2210:
	python -m snewpdag --log INFO snewpdag/data/fd2210.csv --input snewpdag/data/fd_sep_alert.json
	# alternative (need to format the json lines for input):
	# python -m snewpdag --log INFO --jsonlines snewpdag/data/fd2209.csv < snewpdag/data/fd2209b-data.json

snews_pt_subscribe:
	snews_pt subscribe --no-firedrill -p '-m snewpdag snewpdag/data/fd2210.csv --input'

snews_pt_publish:
	for n in 1 2 3 4 5 6 7; do snews_pt publish --no-firedrill fd2209b-msg$n.json; sleep 1; done

init:
	pip install -r requirements.txt

.PHONY: init run test histogram trial trial2 runtest
