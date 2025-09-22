import os, sys
import fontforge

def mergeft(font, A, fin2, rplc=False):
	print('Merging', fin2)
	cmap=culcmap(font)
	print('Loading font2...')
	font2 = fontforge.open(fin2)
	font2.reencode("unicodefull")
	font2.em = font.em
	if A=='A': rmcd='B'
	else: rmcd='A'
	notgl=('.notdef', '.null', 'nonmarkingreturn', 'NULL', 'NUL')
	cmap2=culcmap(font2)
	cmap2={c:cmap2[c] for c in cmap2 if hancheck(c)!=rmcd or c==0x4E00}
	cmap2rev=dict()
	for c,v in cmap2.items():
		if v not in cmap2rev: cmap2rev[v]=list()
		cmap2rev[v].append(c)
	code_codes2 = {}
	for g in cmap2rev.keys():
		if g in notgl: continue
		cs = [c for c in cmap2rev[g] if rplc or c not in cmap]
		if len(cs) > 0:
			code_codes2[cs[0]] = cs[1:]
	font2.selection.select(*code_codes2.keys())
	font2.copy()
	font.selection.select(*code_codes2.keys())
	font.paste()
	print('Adding extra codings...')
	for cd1 in code_codes2.keys():
		if len(code_codes2[cd1]) > 0:
			font[cd1].altuni = code_codes2[cd1]
	font2.close()

def addlk(font, lkn, sl):
	cmap=culcmap(font)
	allc=set(cmap.keys())
	lantgs=list()
	for lantg in ('DFLT', 'cyrl', 'grek', 'hang', 'hani', 'kana', 'latn'):
		lantgs.append((lantg, ("dflt",)))
	lknm, tbnm='lksg'+lkn, 'tbsg'+lkn
	if sl=='s':
		font.addLookup(lknm, 'gsub_single', None, ((lkn, tuple(lantgs)), ))
	elif sl=='l':
		font.addLookup(lknm, 'gsub_ligature', None, ((lkn, tuple(lantgs)), ))
	else: raise
	font.addLookupSubtable(lknm, tbnm)
	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), lkn+'.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			litm=line.strip('\r\n')
			if '\t' not in litm: continue
			s, t=litm.split('\t')
			if sl=='s':
				if s and t and s != t and ord(t) in cmap and ord(s) in cmap:
					gntc = cmap[ord(t)]
					gnsc = cmap[ord(s)]
					if gntc != gnsc:
						font[gnsc].addPosSub(tbnm, gntc)
			else:
				ss=s.split(' ')
				cc=[ord(ch) for ch in ss]
				if ord(t) in cmap and set(cc).issubset(allc):
					wdin=[cmap[c] for c in cc]
					font[cmap[ord(t)]].addPosSub(tbnm, tuple(wdin))

def cklkps(font):
	print('Checking lookups...')
	for lk in font.gsub_lookups:
		font.removeLookup(lk)
	addlk(font, 'vert', 's')
	addlk(font, 'fwid', 's')
	addlk(font, 'dlig', 'l')

def setnm(font, A):
	print('Processing font name...')
	font.os2_vendor='GUIW'
	enname='LanternMing'+A
	tcname='上元明朝'+A
	scname='上元明朝'+A
	janame='上元明朝'+A
	versn='1.04'
	fontVURL='https://github.com/GuiWonder/LanternMing'
	copyright='Copyright(c) LanternMing, 2023-2025.'
	wt='Regular'
	subfamily='Regular'
	font.sfntRevision = float(versn)

	enfml=enname
	tcfml=tcname
	scfml=scname
	jafml=janame
	if wt in ('Regular', 'Bold'):
		enftname=enfml
		tcftname=tcfml
		scftname=scfml
		jaftname=jafml
		enfull=enfml+' '+wt
		tcfull=tcfml+' '+wt
		scfull=scfml+' '+wt
		jafull=jafml+' '+wt
	else:
		enftname=enfull=enfml+' '+wt
		tcftname=tcfull=tcfml+' '+wt
		scftname=scfull=scfml+' '+wt
		jaftname=jafull=jafml+' '+wt
	psname=enfml.replace(' ', '')+'-'+wt
	uniqid=versn+';'+psname
	newname=list()
	newname+=[
		('English (US)', 'Copyright', copyright), 
		('English (US)', 'Family', enftname), 
		('English (US)', 'SubFamily', subfamily), 
		('English (US)', 'UniqueID', uniqid), 
		('English (US)', 'Fullname', enfull), 
		('English (US)', 'Version', 'Version '+versn), 
		('English (US)', 'PostScriptName', psname), 
		('English (US)', 'Vendor URL', fontVURL)
	]
	if wt not in ('Regular', 'Bold'):
		newname+=[
			('English (US)', 'Preferred Family', enfml), 
			('English (US)', 'Preferred Styles', wt), 
		]
	if tcname:
		for lang in ('Chinese (Taiwan)', 'Chinese (Hong Kong)', 'Chinese (Macau)'):
			newname+=[
			(lang, 'Family', tcftname), 
			(lang, 'SubFamily', subfamily), 
			(lang, 'Fullname', tcfull), 
			]
			if wt not in ('Regular', 'Bold'):
				newname+=[
					(lang, 'Preferred Family', tcfml), 
					(lang, 'Preferred Styles', wt), 
				]
	if scname:
		for lang in ('Chinese (PRC)', 'Chinese (Singapore)'):
			newname+=[
			(lang, 'Family', scftname), 
			(lang, 'SubFamily', subfamily), 
			(lang, 'Fullname', scfull), 
			]
			if wt not in ('Regular', 'Bold'):
				newname+=[
					(lang, 'Preferred Family', scfml), 
					(lang, 'Preferred Styles', wt), 
				]
	if janame:
		newname+=[
		('Japanese', 'Family', jaftname), 
		('Japanese', 'SubFamily', subfamily), 
		('Japanese', 'Fullname', jafull), 
		]
		if wt not in ('Regular', 'Bold'):
			newname+=[
				('Japanese', 'Preferred Family', jafml), 
				('Japanese', 'Preferred Styles', wt), 
			]
	font.sfnt_names=tuple(newname)

def culcmap(font):
	cmap=dict()
	for g in font.glyphs():
		if g.unicode>-1:
			cmap[g.unicode]=g.glyphname
		if g.altuni!=None:
			for uni in g.altuni:
				if uni[1]<=0:
					cmap[uni[0]]=g.glyphname
	return cmap

def hancheck(c):
	if cjkcheck(c) in ('Ide', 'A', 'C', 'D', 'E', 'F', 'G', 'H', '0'):
		return 'A'
	if cjkcheck(c) in ('B', 'I', 'J'):
		return 'B'
	else:
		return 'Not'

def cjkcheck(c):
	if c in range(0x4E00, 0x9FFF+1): return 'Ide'
	if c in range(0x3400, 0x4DBF+1): return 'A'
	if c in range(0x20000, 0x2A6DF+1): return 'B'
	if c in range(0x2A700, 0x2B73F+1): return 'C'
	if c in range(0x2B740, 0x2B81F+1): return 'D'
	if c in range(0x2B820, 0x2CEAF+1): return 'E'
	if c in range(0x2CEB0, 0x2EBEF+1): return 'F'
	if c in range(0x30000, 0x3134F+1): return 'G'
	if c in range(0x31350, 0x323AF+1): return 'H'
	if c in range(0x2EBF0, 0x2EE5F+1): return 'I'
	if c in range(0x323B0, 0x3347F+1): return 'J'
	if c==0x3007: return '0'
	return 'Not'

def rmcode(font, A):
	print('Remove codes')
	if A=='A': rmcd='B'
	else: rmcd='A'
	notgl=('.notdef', '.null', 'nonmarkingreturn', 'NULL', 'NUL')
	cmap=culcmap(font)
	cmap={c:cmap[c] for c in cmap if hancheck(c)!=rmcd or c==0x4E00}
	for g in font.glyphs():
		if g.glyphname in notgl: continue
		if g.glyphname not in cmap.values():
			g.removePosSub('*')
			font.removeGlyph(g)
		elif g.altuni!=None:
			lu=list()
			for alt in g.altuni:
				c, u=alt[0], alt[1]
				if u<=0 and (hancheck(c)!=rmcd or c==0x4E00):
					lu.append(alt)
			if len(lu)>0:
				g.altuni=tuple(lu)
			else:
				g.altuni=None

def build(outft, A, fonts):
	print('Target', outft)
	print('Processing...')
	font=fontforge.open(fonts[0])
	font.reencode("unicodefull")
	mergeft(font, A, fonts[1], False)
	mergeft(font, A, fonts[2], True)
	for f in fonts[3:]:
		mergeft(font, A, f, False)
	rmcode(font, A)
	if A=='A':
		cklkps(font)
	setnm(font, A)
	print('Saving', outft)
	font.generate(outft)
	print('Finished')

if __name__ == "__main__":
	build(sys.argv[1], sys.argv[2], sys.argv[3:])
