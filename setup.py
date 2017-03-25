from distutils.core import setup
import py2exe, sys, os

includes = [
"encodings",
"encodings.utf_8"
]

options = {
	"bundle_files":1,
	"compressed":1,
	"optimize":2,
	"includes":includes
}

setup (
	options = {"py2exe":options},
	console = [{'script':"apriori.py"}],
	zipfile= None
)