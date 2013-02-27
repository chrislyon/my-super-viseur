
clean:
	rm -f *.pyc
	rm -f default.log

run:
	python SuperViseur.py

push: clean
	hg commit -u chris 
