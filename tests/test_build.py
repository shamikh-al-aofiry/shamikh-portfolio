from pathlib import Path
import tempfile,shutil,json,subprocess,threading,http.server,socketserver,functools,urllib.request,urllib.error
source=Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory() as tmp:
 r=Path(tmp)/'repo';shutil.copytree(source,r,ignore=shutil.ignore_patterns('dist'))
 def build(): return subprocess.run(['python',str(r/'tools/build.py')],capture_output=True,text=True)
 res=build();assert res.returncode==0,res.stderr
 d=r/'dist'; home=(d/'index.html').read_text();assert '/projects/nims/' in home and '/skills/cisco/' in home and 'project.html?id=' not in home and 'skill.html?id=' not in home
 nim=(d/'projects/nims/index.html').read_text(); assert 'Planned' in nim and 'Isolation Forest' in nim and '(Verified)' not in nim
 assert not (d/'data/profile.json').exists();assert not list(d.rglob('*.yml'))
 print('PASS: generated homepage and 16 concrete direct detail files, planned features labelled, no raw profile/CMS files in output')

 # English-only cleanup and approved homepage content.
 import re
 for file in d.rglob('*'):
  if file.is_file() and file.suffix in ('.html','.js','.css','.json'):
   body=file.read_text(errors='ignore')
   assert not re.search('[\u0600-\u06FF]',body),'Arabic text left in '+str(file)
   for legacy in ('data-copy-ar','data-copy-en','data-i18n','data-alt-ar','data-aria-ar','language-switcher','data-language','portfolio-language','dir="rtl"','lang="ar"'):
    assert legacy not in body,legacy+' left in '+str(file)
 for src in ['index.html','script.js','style.css','projects/index.html','skills/index.html','.pages.yml']:
  assert not re.search('[\u0600-\u06FF]',(r/src).read_text()),'Arabic text left in source '+src
 assert '<html lang="en" dir="ltr">' in home
 assert 'View Portfolio' not in home and 'hero.portfolioAction' not in home
 assert re.search(r'<a class="button button--primary" href="#portfolio"><span>Portfolio</span>',home)
 assert '<a href="#portfolio">Portfolio</a>' in home
 assert 'Selected projects exploring infrastructure, productivity, and design.' not in home
 assert 'hero__field">Information Technology</span> Student' in home and 'Get in Touch' in home and 'Reach out' in home
 assert 'Download Resume' not in home,'resume button must stay hidden without a verified PDF'
 assert 'Explore GitHub Projects' not in home,'GitHub button must stay hidden without a profile URL'
 assert '%' not in ''.join(re.findall(r'<ul class="skill-grid">.*?</ul>',home,re.S)),'no skill percentages'
 card=home[home.index('<article class="project-card project-card--feature'):]
 card=card[:card.index('</article>')]
 order=[card.index(x) for x in ('project-media','project-card__title','project-card__summary','Planned technologies','View Project Details')]
 assert order==sorted(order),'card order must be image, name, description, technologies, details'
 assert 'Implemented technologies' not in card,'planned technologies must not appear as implemented'
 assert '/projects/nims/' in card
 print('PASS: English-only output, Portfolio button, approved hero/contact copy, card order, honest technologies')
 class Handler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*a): pass
 handler=functools.partial(Handler,directory=str(d))
 with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
  threading.Thread(target=server.serve_forever,daemon=True).start(); root=f'http://127.0.0.1:{server.server_address[1]}'
  for path in ['/','/projects/nims/','/skills/cisco/']:
   with urllib.request.urlopen(root+path) as response: assert response.status==200
  try:urllib.request.urlopen(root+'/projects/nonexistent/')
  except urllib.error.HTTPError as e: assert e.code==404
  else:raise AssertionError('unknown route')
  server.shutdown()
 print('PASS: local HTTP direct links and unknown URL 404 (GitHub Pages custom 404 not deployed/tested)')
 path=r/'data/projects/taskflow-pro.json'; task=json.loads(path.read_text()); task['status']='draft';task['cover']='/media/projects/secret.png';path.write_text(json.dumps(task))
 (r/'media/projects').mkdir(parents=True,exist_ok=True);(r/'media/projects/secret.png').write_bytes(b'private fake image')
 archived=r/'data/skills/docker.json';doc=json.loads(archived.read_text());doc['status']='archived';archived.write_text(json.dumps(doc))
 res=build();assert res.returncode==0,res.stderr
 assert not (d/'projects/taskflow-pro').exists() and not (d/'skills/docker').exists() and not (d/'media/projects/secret.png').exists()
 assert 'TaskFlow Pro' not in (d/'data/projects.json').read_text() and '/projects/taskflow-pro/' not in (d/'index.html').read_text()
 assert not any('TaskFlow Pro' in file.read_text(errors='ignore') for file in d.rglob('*') if file.is_file())
 print('PASS: draft and archived pages, JSON, homepage links, draft-only media excluded')
 task['status']='published';task['cover']='';task['skills']=['cisco'];path.write_text(json.dumps(task));res=build();assert res.returncode==0,res.stderr
 assert '/skills/cisco/' in (d/'projects/taskflow-pro/index.html').read_text()
 assert '/projects/taskflow-pro/' in (d/'skills/cisco/index.html').read_text()
 print('PASS: one CMS relationship appears on both published detail pages')
 task['skills']=['missing'];path.write_text(json.dumps(task));res=build();assert res.returncode!=0 and 'Unknown skill reference' in res.stderr
 print('PASS: broken relationship fails build')
 task['skills']=[];task['cover']='/media/projects/missing.png';path.write_text(json.dumps(task));res=build();assert res.returncode!=0
 print('PASS: missing referenced published image fails build')
 task['cover']='';path.write_text(json.dumps(task));profile=r/'data/profile.json';pr=json.loads(profile.read_text());pr['resume_pdf']='/media/cv/cv.pdf';pr['resume_verified']=True;profile.write_text(json.dumps(pr));(r/'media/cv').mkdir(exist_ok=True);(r/'media/cv/cv.pdf').write_bytes(b'');res=build();assert res.returncode!=0
 print('PASS: empty resume rejected')
 for file in (r/'data').rglob('*.json'):json.loads(file.read_text())
 print('PASS: all source content JSON parses')
 profile=r/'data/profile.json';pr=json.loads(profile.read_text());pr['resume_verified']=False;pr['resume_pdf']='';pr['github']='https://github.com/example-user';profile.write_text(json.dumps(pr));res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text();assert 'Explore GitHub Projects' in home and 'href="https://github.com/example-user"' in home and 'aria-label="GitHub"' in home
 print('PASS: GitHub profile URL enables Other Projects and the contact icon')
 pdf=b'%PDF-1.4\n'+b'0'*200+b'\n%%EOF\n';(r/'media/cv/cv.pdf').write_bytes(pdf);pr['resume_pdf']='/media/cv/cv.pdf';pr['resume_verified']=True;profile.write_text(json.dumps(pr));res=build();assert res.returncode==0,res.stderr
 assert 'href="/media/cv/cv.pdf" download' in (d/'index.html').read_text() and (d/'media/cv/cv.pdf').exists()
 print('PASS: verified resume PDF enables Download Resume')
 task['github_url']='https://github.com/example-user/taskflow';path.write_text(json.dumps(task));res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text();assert 'aria-label="TaskFlow Pro repository on GitHub"' in home and 'GitHub Repository' in home
 print('PASS: project github_url links the card image and adds a repository button')
 legacy=r/'data/skills/cisco.json';sk=json.loads(legacy.read_text());sk['description']={'en':'x','ar':'y'};legacy.write_text(json.dumps(sk));res=build();assert res.returncode!=0 and 'plain text' in res.stderr
 print('PASS: leftover bilingual objects fail the build')

# ---------- Skills icons, project links, Other Projects, CMS schema and responsive wiring ----------
import importlib.util
with tempfile.TemporaryDirectory() as tmp:
 r=Path(tmp)/'repo';shutil.copytree(source,r,ignore=shutil.ignore_patterns('dist'))
 d=r/'dist'
 def build(): return subprocess.run(['python',str(r/'tools/build.py')],capture_output=True,text=True)
 def edit(rel,**kw):
  f=r/rel;obj=json.loads(f.read_text());obj.update(kw);f.write_text(json.dumps(obj));return obj
 res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text()
 grid=re.search(r'<ul class="skill-grid">(.*?)</ul>',home,re.S).group(1)
 assert grid.count('class="skill-glyph"')==13 and 'skill-monogram' not in grid,'every published skill shows its built-in icon'
 assert 'skill-tile__icon--large' in (d/'skills/cisco/index.html').read_text() and 'skill-glyph' in (d/'skills/cisco/index.html').read_text()
 spec=importlib.util.spec_from_file_location('b',r/'tools/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 cms=json.loads((r/'.pages.yml').read_text());content={e['name']:e for e in cms['content']}
 fields=lambda e:{f['name']:f for f in content[e]['fields']}
 keys={v['name'] for v in fields('skills')['icon_key']['options']['values']}-{''}
 assert keys==set(b.SKILL_GLYPHS),'CMS built-in icon options must match the glyph library'
 for f in (r/'data/skills').glob('*.json'): assert json.loads(f.read_text()).get('icon_key','') in keys|{''}
 print('PASS: built-in skill icons on tiles and detail pages; CMS icon options match the build')
 (r/'media/skills').mkdir(parents=True,exist_ok=True);(r/'media/skills/cisco.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>')
 edit('data/skills/cisco.json',icon='/media/skills/cisco.svg');res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text();tile=home[home.index('href="/skills/cisco/"'):];tile=tile[:tile.index('</li>')]
 assert 'skill-tile__icon--logo' in tile and 'src="/media/skills/cisco.svg"' in tile and 'skill-glyph' not in tile and (d/'media/skills/cisco.svg').exists()
 edit('data/skills/cisco.json',icon='',icon_key='not-an-icon');res=build();assert res.returncode!=0 and 'Unknown built-in skill icon' in res.stderr
 edit('data/skills/cisco.json',icon_key='');res=build();assert res.returncode==0 and 'skill-monogram' in (d/'index.html').read_text()
 edit('data/skills/cisco.json',icon_key='network-switch')
 print('PASS: uploaded official icon overrides the glyph; unknown icon fails; empty falls back to a monogram')
 res=build();home=(d/'index.html').read_text()
 assert 'href="https://task-manager-pro-lemon.vercel.app/"' in home,'checked live demo is shown'
 assert 'smart-design-pro-qh3e3' not in home,'unchecked live demo stays hidden'
 assert '<section class="other-projects"' not in home,'Other Projects hidden with no GitHub URL and no extra projects'
 edit('data/projects/smart-design-pro.json',featured=False,github_url='https://github.com/example-user/smart-design');res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text();other=home[home.index('<section class="other-projects"'):];other=other[:other.index('</section>')]
 assert 'Smart Design Pro' in other and '/projects/smart-design-pro/' in other and 'https://github.com/example-user/smart-design' in other and 'Explore GitHub Projects' not in other
 assert 'project-card__title">Smart Design Pro' not in home,'non-featured project is not a large card'
 assert (d/'projects/smart-design-pro/index.html').exists() and 'GitHub Repository' in (d/'projects/smart-design-pro/index.html').read_text()
 print('PASS: verified live demo only; non-featured projects listed under Other Projects with repository links')
 edit('data/projects/taskflow-pro.json',github_url='http://github.com/x/y');res=build();assert res.returncode!=0 and 'Invalid github_url' in res.stderr
 edit('data/projects/taskflow-pro.json',github_url='',live_verified=True,live_url='');res=build();assert res.returncode!=0 and 'Live demo' in res.stderr
 edit('data/projects/taskflow-pro.json',live_url='https://task-manager-pro-lemon.vercel.app/')
 print('PASS: invalid repository URL and checked-but-empty live demo fail the build')
 edit('data/projects/taskflow-pro.json',order=0);res=build();assert res.returncode==0,res.stderr
 home=(d/'index.html').read_text();assert home.index('project-card__title">TaskFlow Pro')<home.index('project-card__title">NIM&amp;S'),'display order controls card order'
 edit('data/projects/taskflow-pro.json',status='draft');res=build();assert '/projects/taskflow-pro/' not in (d/'index.html').read_text() and not (d/'projects/taskflow-pro').exists()
 (r/'data/projects/taskflow-pro.json').unlink();res=build();assert res.returncode==0,res.stderr
 print('PASS: CMS order, hide (draft) and delete all reflect in the build')
 pf=fields('projects')
 for k in ('github_url','live_url','live_verified','order','featured','status','skills'): assert k in pf,k
 assert {v['name'] for v in pf['status']['options']['values']}=={'draft','published','archived'}
 v=content['projects']['view'];assert v['default']=={'sort':'order','order':'asc'} and 'order' in v['sort']
 assert content['projects']['operations']=={'create':True,'rename':False,'delete':True}
 for k in ('id','slug','github_url','live_url'): assert 'pattern' in pf[k],k
 assert re.fullmatch(pf['github_url']['pattern']['regex'],'https://github.com/user/repo') and not re.fullmatch(pf['github_url']['pattern']['regex'],'http://github.com/user/repo') and re.fullmatch(pf['github_url']['pattern']['regex'],'')
 print('PASS: Pages CMS projects schema: links, ordering, hide/delete, validation patterns')
 js=(r/'script.js').read_text();css=(r/'style.css').read_text()
 q=re.search(r"MOBILE_QUERY = '(\(max-width: [\d.]+rem\))'",js).group(1)
 assert '@media '+q+' {' in css,'phone breakpoint in CSS must match the menu script'
 for page in [d/'index.html',*d.glob('projects/*/index.html'),*d.glob('skills/*/index.html'),d/'404.html']:
  assert 'name="viewport" content="width=device-width, initial-scale=1"' in page.read_text(),page
 print('PASS: responsive wiring: one shared phone breakpoint, viewport meta on every page')
