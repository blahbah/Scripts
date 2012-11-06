# Q&D TomBoy to HTML Export
# Creates one .html file for each TomBoy notebook in your notes folder, with a table of contents at the top
# links between notebooks are preserved
from xml.dom import minidom
import os, io
script_path = os.path.dirname(__file__)
# <parameters>
# every html file will be created in this directory, existing files will be overwritten
export_path = script_path
# incomplete list of tomboy tags found in some notes, to be replaced by corresponding html (any attribute in those tags is ignored)
replace_tags = {
	'datetime': ('<span style="color: grey; font-size: small">', '</span>'),
	'size:small': ('<span style="font-size: small">', '</span>'),
	'bold': ('<span style="font-weight: bold">', '</span>'),
	'highlight': ('<span style="background-color: yellow">', '</span>'),
	'list': ('<ul>', '</ul>'),
	'list-item': ('<li>', '</li>'),
}
# </parameters>

def recurse_read_nodes(node):
	ret = ''
	for n in node.childNodes:
		if n.nodeType == minidom.Document.TEXT_NODE:
			ret += n.data
		elif n.nodeType == minidom.Document.ELEMENT_NODE:
			if replace_tags.has_key(n.tagName):
				ret += (replace_tags[n.tagName][0]
					+ recurse_read_nodes(n)
					+ replace_tags[n.tagName][1])
			elif 'link:' in n.tagName:
				# tags link:url, link:internal or link:broken
				try:
					link_name = n.childNodes[0].data
				except (IndexError, AttributeError):
					link_name = "*** TOMBOY EXPORT ERROR: can't read link ***"
				if n.tagName == 'link:internal':
					link_url = notes[link_name.upper()][0] + '.html' if notebook_name != notes[link_name.upper()][0] else ''
					link_url += '#' + link_name
				elif n.tagName == 'link:broken':
					link_url = '#' + link_name
				else:
					link_url = link_name
				ret += '<a href="' + link_url + '">' + link_name + '</a>'
	return ret

# dictionary containing the final html for every notebook
# 	notebooks['notebook_name'] = ['table of contents', 'all notes']
notebooks = {}
notebook_name = ''
note_title = ''
# TomBoy notes directory
dirpath = os.path.join(os.environ['APPDATA'], 'Tomboy', 'notes')
# list of all notes' files
file_paths = [fpath for fpath in os.listdir(dirpath) if fpath <> 'Backup' and fpath.endswith('.note')]
# 1st pass: read every .note file and make a "bidirectional" dictionary "file_name <-> note_title" in order to preserve internal links in different notebooks
notes = {}
for fpath in file_paths:
	try:
		xmldoc = minidom.parse(os.path.join(dirpath, fpath))
	except IOError:
		sys.stderr.writelines("can't read file " + fpath)
		continue
	notebook_name = 'Notes'
	for n in xmldoc.getElementsByTagName('tag'):
		try:
			if n.childNodes[0].data.startswith('system:notebook:'):
				notebook_name = n.childNodes[0].data[16:]
		except AttributeError:
			pass
	if not notebooks.has_key(notebook_name):
		notebooks[notebook_name] = ['', '']
	note_title = "*** TOMBOY EXPORT ERROR: can't find note title ***"
	try:
		note_title = xmldoc.getElementsByTagName('title')[0].childNodes[0].data
	except AttributeError:
		pass
	# the goal is to be able to find the note's title from its file name and vice versa, and also the notebook's name
	# (there must be a better way to do this)
	notes[note_title.upper()] = [notebook_name, fpath]
	notes[fpath] = [notebook_name, note_title]
# 2nd pass: convert notes' content to html
for fpath in file_paths:
	note_title = notes[fpath][1]
	notebook_name = notes[fpath][0]
	# sys.stdout.writelines(fpath + ' -> ' + notebook_name + ' / ' + note_title)
	try:
		xmldoc = minidom.parse(os.path.join(dirpath, fpath))
	except IOError:
		sys.stderr.writelines("can't read file " + fpath)
		continue
	note_content_node = xmldoc.getElementsByTagName('note-content')[0]
	note_content_text = recurse_read_nodes(note_content_node)
	notebooks[notebook_name][0] += '<a href="#' + note_title + '">' + note_title + '</a>\n'
	notebooks[notebook_name][1] += '<a name="' + note_title + '">&nbsp;</a><hr /><!--' + fpath + '--><a href="#TomBoyExportNoteList" style="font-size: 50%; vertical-align: super">^(up)</a><br>' + note_content_text
# write final .html files
for k in notebooks:
	with io.open(os.path.join(export_path, k + '.html'), 'w') as f:
		f.write('<html><body style="font-family: monospace; white-space: pre-wrap"><a name="TomBoyExportNoteList">&nbsp;</a><hr />' + notebooks[k][0] + notebooks[k][1] + '</body></html>')
		f.close()

# TomBoy tag list as seen in a few notes in version 1.8.3
# note
	# title
	# text
		# note-content
			# datetime -> grey and small (Ctrl+D)
			# list -> <ul>
				# list-item -> <li>
			# size:small
			# link:url -> external link
			# link:internal -> contains only the name of a note, in any notebook
			# link:broken -> same, but the note doesn't exist
			# bold
			# highlight -> yellow background
	# create-date
	# last-change-date
	# last-metadata-change-date
	# cursor-position
	# selection-bound-position
	# width
	# height
	# x
	# y
	# tags
		# tag -> contains system:notebook:notebook_name
	# open-on-startup
# The list was made using this script:
# from xml.dom import minidom
# import os
# def recurse_tag_list(tag_list, xml_node):
	# for n in xml_node.childNodes:
		# if n.nodeType == minidom.Document.ELEMENT_NODE:
			# tag_list.add(n.tagName)
			# recurse_tag_list(tag_list, n)
# dirpath = os.path.join(os.environ['APPDATA'], 'Tomboy', 'notes')
# file_paths = [os.path.join(d, f) for (d,ds,fs) in os.walk(dirpath) for f in fs]
# tags = set()
# for fpath in file_paths:
	# xmldoc = minidom.parse(fpath)
	# recurse_tag_list(tags, xmldoc)
# sys.stdout.write('\n'.join(tags))
# raw_input()
