.PHONY: calculator

generated-transitions: transitions_generator.py src/table_synthesis/compiler.py
	python transitions_generator.py ./input.txt > src/analysis/task_transitions.py

bootstrap: transitions_generator.py src/table_synthesis/compiler.py
	python transitions_generator.py ./bootstrap.txt > src/analysis/bootstrapped_transitions.py

calculator: calculator.py
	python calculator.py
