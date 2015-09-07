# PyDBLP2Cayley
Python code parses DBLP and stores researchers' publication relationships on Cayley, a graph database which accelerates the speed of queries on the publications relationship among researchers.

Publication relationship is co-authorship between two researchers.

Notes:
 - File required: dblp.xml, dblp.dtd (The newest file could be found at http://dblp.uni-trier.de/xml/)
 - Cayley, a graph-based database should be installed and launched before running this script (https://github.com/google/cayley)
 - Time: it takes me around 1-2 days with a normal PC

Currently, books in dblp are not considered as part of publications relationships. 
