import os, sys
import fontforge

def ckrge(cd, A):
	if A=='A':
		if cd in range(0x20000, 0x2A6DF+1):
			return True
		return False
	elif cd in range(0x4E01, 0x9FFF+1) or cd in range(0x3400, 0x4DBF+1) or cd in range(0x2A700, 0x2B73F+1) or cd in range(0x2B740, 0x2B81F+1) or cd in range(0x2B820, 0x2CEAF+1) or cd in range(0x2CEB0, 0x2EBEF+1) or cd in range(0x30000, 0x3134F+1) or cd in range(0x31350, 0x323AF+1):
		return True
	return False

def rmglA(font, A):
	notgl=('.notdef', '.null', 'nonmarkingreturn', 'NULL', 'NUL')
	for gls in font.glyphs():
		if gls.glyphname in notgl:continue
		gls.altuni = None
	code_glyph, glyph_codes=getallcodesname(font)
	for gl in glyph_codes:
		glyph_codes[gl]=[cd for cd in glyph_codes[gl] if not ckrge(cd, A)]
	useg=set()
	for gls in font.glyphs():
		if gls.glyphname not in notgl and len(glyph_codes[gls.glyphname])<1:
			gls.removePosSub('*')
			font.removeGlyph(gls)

def getallcodesname(thfont):
	c_g = dict()
	g_c=dict()
	for gls in thfont.glyphs():
		g_c[gls.glyphname]=list()
		if gls.unicode > -1:
			c_g[gls.unicode]=gls.glyphname
			g_c[gls.glyphname].append(gls.unicode)
		if gls.altuni != None:
			for uni in gls.altuni:
				if uni[1] <= 0:
					c_g[uni[0]] = gls.glyphname
					g_c[gls.glyphname].append(uni[0])
	return c_g, g_c

def mergeft(font, fin2, rplc=False):
	print('Loading font2...')
	code_glyph, glyph_codes=getallcodesname(font)
	font2 = fontforge.open(fin2)
	font2.reencode("unicodefull")
	font2.em = font.em
	print('Getting glyph2 codes')
	code_glyph2, glyph_codes2=getallcodesname(font2)
	print('Adding glyphs...')
	code_codes2 = {}
	for n2 in glyph_codes2.keys():
		lc = [ac1 for ac1 in glyph_codes2[n2] if rplc or ac1 not in code_glyph]
		if len(lc) > 0:
			code_codes2[lc[0]] = lc[1:]
	font2.selection.select(*code_codes2.keys())
	font2.copy()
	font.selection.select(*code_codes2.keys())
	font.paste()
	print('Adding extra codings...')
	for cd1 in code_codes2.keys():
		if len(code_codes2[cd1]) > 0:
			font[cd1].altuni = code_codes2[cd1]
	del code_codes2
	del glyph_codes2
	del code_glyph2
	font2.close()
def addsglk(font, lkn):
	code_glyph, glyph_codes=getallcodesname(font)
	lantgs=list()
	for lantg in ('DFLT', 'cyrl', 'grek', 'hang', 'hani', 'kana', 'latn'):
		lantgs.append((lantg, ("dflt",)))
	lknm, tbnm='lksg'+lkn, 'tbsg'+lkn
	font.addLookup(lknm, 'gsub_single', None, ((lkn, tuple(lantgs)), ))
	font.addLookupSubtable(lknm, tbnm)
	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), lkn+'.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			litm=line.strip('\r\n')
			if '\t' not in litm: continue
			s, t=litm.split('\t')
			if s and t and s != t and ord(t) in code_glyph and ord(s) in code_glyph:
				gntc = code_glyph[ord(t)]
				gnsc = code_glyph[ord(s)]
				if gntc != gnsc:
					font[gnsc].addPosSub(tbnm, gntc)
def addlglk(font, lkn):
	code_glyph, glyph_codes=getallcodesname(font)
	lantgs=list()
	for lantg in ('DFLT', 'cyrl', 'grek', 'hang', 'hani', 'kana', 'latn'):
		lantgs.append((lantg, ("dflt",)))
	lknm, tbnm='lksg'+lkn, 'tbsg'+lkn
	font.addLookup(lknm, 'gsub_ligature', None, ((lkn, tuple(lantgs)), ))
	font.addLookupSubtable(lknm, tbnm)
	with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), lkn+'.txt'), 'r', encoding = 'utf-8') as f:
		for line in f.readlines():
			litm=line.strip('\r\n')
			if '\t' not in litm: continue
			wdin=list()
			s, t=litm.split('\t')
			if ord(t) not in code_glyph:continue
			ss=s.split(' ')
			for ch in ss:
				if ord(ch) in code_glyph:
					wdin.append(code_glyph[ord(ch)])
				else:
					wdin.clear()
					break
			if not wdin:continue
			font[code_glyph[ord(t)]].addPosSub(tbnm, tuple(wdin))

def cklkps(font):
	for lk in font.gsub_lookups:
		font.removeLookup(lk)
	addsglk(font, 'vert')
	addsglk(font, 'fwid')
	addlglk(font, 'dlig')

def setnm(font, A):
	ennm='LanternMing'+A
	tcnm='上元明朝'+A
	scnm='上元明朝'+A
	jpnm='上元明朝'+A
	versn='1.00'
	fontVURL='https://github.com/GuiWonder/LanternMing'
	wt='Regular'

	if not versn:
		versn='{:.2f}'.format(font.sfntRevision)
	else:
		font.sfntRevision = float(versn)
	fmlName=ennm
	ftName=ennm
	ftNamesc=scnm
	ftNametc=tcnm
	ftNamejp=jpnm
	subfamily='Regular'
	psName=fmlName.replace(' ', '')+'-'+wt
	uniqID=versn+';'+psName
	#if wt=='Bold':
	if wt in ('Regular', 'Bold'):
		fullName=ftName+' '+wt
		fullNamesc=ftNamesc+' '+wt
		fullNametc=ftNametc+' '+wt
		fullNamejp=ftNamejp+' '+wt
	else:
		fullName=ftName
		fullNamesc=ftNamesc
		fullNametc=ftNametc
		fullNamejp=ftNamejp
	newname=list()
	newname+=[
		('English (US)', 'Copyright', 'Copyright(c) LanternMing, 2023.'), 
		('English (US)', 'Family', ftName), 
		('English (US)', 'SubFamily', subfamily), 
		('English (US)', 'UniqueID', uniqID), 
		('English (US)', 'Fullname', fullName), 
		('English (US)', 'Version', 'Version '+versn), 
		('English (US)', 'PostScriptName', psName), 
		('English (US)', 'Vendor URL', fontVURL)
	]
	if wt not in ('Regular', 'Bold'):
		newname+=[
			('English (US)', 'Preferred Family', fmlName), 
			('English (US)', 'Preferred Styles', wt), 
		]
	if tcnm:
		for lang in ('Chinese (Taiwan)', 'Chinese (Hong Kong)', 'Chinese (Macau)'):
			newname+=[
			(lang, 'Family', ftNametc), 
			(lang, 'SubFamily', subfamily), 
			(lang, 'Fullname', fullNametc), 
			]
			if wt not in ('Regular', 'Bold'):
				newname+=[
					(lang, 'Preferred Family', tcnm), 
					(lang, 'Preferred Styles', wt), 
				]
	if scnm:
		for lang in ('Chinese (PRC)', 'Chinese (Singapore)'):
			newname+=[
			(lang, 'Family', ftNamesc), 
			(lang, 'SubFamily', subfamily), 
			(lang, 'Fullname', fullNamesc), 
			]
			if wt not in ('Regular', 'Bold'):
				newname+=[
					(lang, 'Preferred Family', scnm), 
					(lang, 'Preferred Styles', wt), 
				]
	if jpnm:
		newname+=[
		('Japanese', 'Family', ftNamejp), 
		('Japanese', 'SubFamily', subfamily), 
		('Japanese', 'Fullname', fullNamejp), 
		]
		if wt not in ('Regular', 'Bold'):
			newname+=[
				('Japanese', 'Preferred Family', jpnm), 
				('Japanese', 'Preferred Styles', wt), 
			]
	font.sfnt_names=tuple(newname)

def build(outft, A, fonts):
	print('Target', outft)
	print('Processing...')
	font=fontforge.open(fonts[0])
	font.reencode("unicodefull")
	print('Merging glyphs...')
	mergeft(font, fonts[1], False)
	print('Merging glyphs...')
	mergeft(font, fonts[2], True)
	print('Checking glyphs...')
	rmglA(font, A)
	if A=='A':
		print('Checking lookups...')
		cklkps(font)
	print('Processing font name...')
	setnm(font, A)
	print('Saving...')
	font.generate(outft)
	print('Finished', outft)

if __name__ == "__main__":
	build(sys.argv[1], sys.argv[2], sys.argv[3:])
