#!/usr/bin/env python3
"""Generate a static, published-only GitHub Pages artifact using Python's standard library."""
import html, json, os, re, shutil, sys
from pathlib import Path
from urllib.parse import urlparse
R=Path(__file__).resolve().parent.parent
OUT=R/'dist'
REPOSITORY=os.environ.get('GITHUB_REPOSITORY','').strip()
REPOSITORY_NAME=REPOSITORY.rsplit('/',1)[-1] if REPOSITORY else ''
BASE_PATH='' if not REPOSITORY_NAME or REPOSITORY_NAME.endswith('.github.io') else '/'+REPOSITORY_NAME
E=lambda value: html.escape(str(value or ''), quote=True)

def site_path(path):
    """Prefix an internal absolute path with the GitHub Pages project path when needed."""
    return BASE_PATH+'/'+str(path).lstrip('/')

def prefix_root_urls(source):
    """Prefix root-relative href/src attributes in source templates, not generated body HTML."""
    if not BASE_PATH: return source
    return re.sub(r"((?:href|src)=['\"]) /(?!/)".replace(' ',''), lambda m: m.group(1)+BASE_PATH+'/', source)

def read(path):
    with open(path,encoding='utf8') as f: return json.load(f)

def txt(value):
    """Content fields are plain English strings."""
    if value is None: return ''
    if isinstance(value,(dict,list)): raise ValueError('Expected plain text, found structured value: '+json.dumps(value,ensure_ascii=False)[:80])
    return str(value).strip()

def valid_url(url):
    if not url: return ''
    p=urlparse(str(url)); return str(url) if p.scheme=='https' and p.netloc and not p.username and not p.password else ''

def media(value,exts=None):
    if not value: return ''
    rel=str(value).lstrip('/')
    if not rel.startswith('media/') or '\\' in rel or '..' in Path(rel).parts: raise ValueError('Unsafe media path: '+rel)
    path=(R/rel).resolve(); root=(R/'media').resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.is_symlink(): raise ValueError('Missing or unsafe media: '+rel)
    if exts and path.suffix.lower() not in exts: raise ValueError('Unsupported media format: '+rel)
    out=OUT/rel; out.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,out)
    return site_path(rel)

IMG={'.jpg','.jpeg','.png','.webp','.gif','.avif','.svg'}
DOC=IMG|{'.pdf'}
STATUSES={'planned':'Planned','implemented':'Implemented','verified':'Verified'}
STAGES={'':'','planning':'Planning','in-progress':'In progress','completed':'Completed'}

def records(folder):
    result=[]; ids=set(); slugs=set()
    for f in sorted((R/'data'/folder).glob('*.json')):
        obj=read(f); ident=obj.get('id',''); slug=obj.get('slug','')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',ident) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug): raise ValueError(f'Invalid id or slug: {f.name}')
        if ident in ids or slug in slugs: raise ValueError('Duplicate id or slug: '+f.name)
        if obj.get('status') not in ('draft','published','archived'): raise ValueError('Invalid publication status: '+f.name)
        if not obj.get('name'): raise ValueError('Missing name: '+f.name)
        if obj.get('stage','') not in STAGES: raise ValueError('Invalid project stage: '+f.name)
        ids.add(ident); slugs.add(slug); result.append(obj)
    return sorted(result,key=lambda x:(float(x.get('order',0)),x['id']))

def details_url(kind,item): return site_path(kind+'/'+item['slug']+'/')

# ---------- Icons (hand-drawn line icons plus the official GitHub and LinkedIn marks) ----------
ICONS={
 'arrow-right':('0 0 24 24','<path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
 'arrow-left':('0 0 24 24','<path d="M19 12H5M11 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
 'download':('0 0 24 24','<path d="M12 4v10.5M7.5 10 12 14.5 16.5 10M5 19h14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
 'external':('0 0 24 24','<path d="M14 5h5v5M19 5l-8 8M17 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'),
 'mail':('0 0 24 24','<rect x="3" y="5" width="18" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="m4 7.5 8 5.5 8-5.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'),
 'telegram':('0 0 24 24','<path d="M20.5 4.5 3.5 11.2l5.6 2.1 2.2 6.2 3.1-4 4.7 3.5 1.4-14.5ZM9.1 13.3l8.4-6.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'),
 'github':('0 0 16 16','<path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>'),
 'linkedin':('0 0 24 24','<path fill="currentColor" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 4.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.125 2.062 2.062 0 0 1 0 4.125zM7.119 20.452H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'),
}
def icon(name,cls='icon'):
    box,inner=ICONS[name]
    return f'<svg class="{cls}" viewBox="{box}" width="20" height="20" aria-hidden="true" focusable="false">{inner}</svg>'

# ---------- Conceptual cover artwork (never screenshots) ----------
def concept_art(project):
    pid=project['id']
    if pid=='nims':
        nodes=[(70,150),(170,80),(170,220),(290,150),(400,70),(400,230),(500,150)]
        edges=[(0,1),(0,2),(1,3),(2,3),(3,4),(3,5),(4,6),(5,6),(1,4)]
        lines=''.join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}"/>' for a,b in edges)
        dots=''.join(f'<circle cx="{x}" cy="{y}" r="{14 if i==3 else 8}"/>' for i,(x,y) in enumerate(nodes))
        return f'<svg class="concept-art concept-art--network" viewBox="0 0 570 300" preserveAspectRatio="xMidYMid meet" aria-hidden="true"><g class="concept-art__lines">{lines}</g><g class="concept-art__nodes">{dots}</g><circle class="concept-art__pulse" cx="290" cy="150" r="30"/></svg>'
    if pid=='taskflow-pro':
        rows=''.join(f'<g transform="translate(150 {62+i*48})"><rect class="concept-art__row" width="270" height="34" rx="9"/><circle class="concept-art__check{" is-done" if i<2 else ""}" cx="20" cy="17" r="8"/><rect class="concept-art__bar" x="40" y="13" width="{[150,190,120,170][i]}" height="8" rx="4"/></g>' for i in range(4))
        return f'<svg class="concept-art concept-art--tasks" viewBox="0 0 570 300" preserveAspectRatio="xMidYMid meet" aria-hidden="true">{rows}</svg>'
    if pid=='smart-design-pro':
        return ('<svg class="concept-art concept-art--design" viewBox="0 0 570 300" preserveAspectRatio="xMidYMid meet" aria-hidden="true">'
                '<rect class="concept-art__frame" x="150" y="60" width="200" height="150" rx="16"/>'
                '<rect class="concept-art__frame concept-art__frame--front" x="220" y="95" width="200" height="150" rx="16"/>'
                '<circle class="concept-art__node" cx="220" cy="95" r="6"/><circle class="concept-art__node" cx="420" cy="245" r="6"/>'
                '<path class="concept-art__spark" d="M455 70l6 16 16 6-16 6-6 16-6-16-16-6 16-6z"/></svg>')
    initial=E(project['name'][:1])
    return f'<svg class="concept-art" viewBox="0 0 570 300" aria-hidden="true"><text x="285" y="190" text-anchor="middle" class="concept-art__initial">{initial}</text></svg>'

def project_media(p,eager=False):
    cover=p.get('cover'); name=txt(p['name'])
    if cover:
        return f'<img src="{E(media(cover,IMG))}" alt="{E(name)} cover image" loading="{"eager" if eager else "lazy"}" decoding="async">'
    label='Concept illustration' if p.get('stage') in ('planning','in-progress') else 'Cover placeholder'
    return concept_art(p)+f'<figcaption class="project-media__caption">{label}</figcaption>'

def badges(p):
    out=''
    if txt(p.get('context')): out+=f'<span class="badge">{E(txt(p.get("context")))}</span>'
    stage=STAGES.get(p.get('stage',''),'')
    if stage: out+=f'<span class="badge badge--stage badge--{E(p["stage"])}">{E(stage)}</span>'
    return out

def tech_groups(p):
    done=[];planned=[]
    for entry in p.get('technologies') or []:
        status=entry.get('status')
        if status not in STATUSES: raise ValueError('Feature or technology requires an explicit valid status')
        label=txt(entry.get('text'))
        if label: (planned if status=='planned' else done).append(label)
    return done,planned

def tag_list(items,limit=None,planned=False,more_href=''):
    shown=items if limit is None else items[:limit]
    cls='tag tag--planned' if planned else 'tag'
    lis=''.join(f'<li class="{cls}">{E(t)}</li>' for t in shown)
    if limit is not None and len(items)>limit:
        lis+=f'<li class="tag tag--more"><a href="{E(more_href)}">+{len(items)-limit} more</a></li>'
    return f'<ul class="tag-list">{lis}</ul>'

def tech_block(p,limit=None,more_href=''):
    done,planned=tech_groups(p); out=''
    if done: out+=f'<div class="tech-group"><p class="tech-group__label">Implemented technologies</p>{tag_list(done,limit,False,more_href)}</div>'
    if planned: out+=f'<div class="tech-group"><p class="tech-group__label">Planned technologies</p>{tag_list(planned,limit,True,more_href)}</div>'
    return f'<div class="project-tech">{out}</div>' if out else ''

def project_links(p,compact=False):
    links=''
    github=valid_url(p.get('github_url'))
    live=valid_url(p.get('live_url')) if p.get('live_verified') is True else ''
    if github: links+=f'<a class="button button--quiet" href="{E(github)}" rel="noopener noreferrer" target="_blank">{icon("github")}<span>GitHub Repository</span></a>'
    if live: links+=f'<a class="button button--quiet" href="{E(live)}" rel="noopener noreferrer" target="_blank">{icon("external")}<span>Live Demo</span></a>'
    if not compact:
        video=valid_url(p.get('video_url'))
        if video: links+=f'<a class="button button--quiet" href="{E(video)}" rel="noopener noreferrer" target="_blank">{icon("external")}<span>Video</span></a>'
    return links

def project_card(p,feature=False,index=0):
    name=txt(p['name']); detail=details_url('projects',p); github=valid_url(p.get('github_url'))
    figure=f'<figure class="project-media project-media--{E(p["id"])}">{project_media(p)}</figure>'
    if github:
        hint=f'<span class="project-card__repo-hint" aria-hidden="true">{icon("github")}<span>View repository</span></span>'
        figure=f'<a class="project-card__media-link" href="{E(github)}" rel="noopener noreferrer" target="_blank" aria-label="{E(name)} repository on GitHub">{figure}{hint}</a>'
    full=txt(p.get('full_name')); summary=txt(p.get('summary'))
    head=f'<div class="project-card__head"><h3 class="project-card__title">{E(name)}</h3>{badges(p)}</div>'
    body=head+(f'<p class="project-card__fullname">{E(full)}</p>' if full else '')+(f'<p class="project-card__summary">{E(summary)}</p>' if summary else '')
    body+=tech_block(p,limit=6 if feature else 4,more_href=detail)
    body+=f'<div class="project-card__actions"><a class="button button--primary button--small" href="{E(detail)}" aria-label="View project details: {E(name)}"><span>View Project Details</span>{icon("arrow-right")}</a>{project_links(p,compact=True)}</div>'
    cls='project-card project-card--feature' if feature else 'project-card'
    return f'<article class="{cls} reveal" style="--i:{index}">{figure}<div class="project-card__body">{body}</div></article>'

def monogram(name):
    caps=re.findall(r'[A-Z]',name); words=[w for w in re.split(r'[\s/]+',name) if w]
    if len(name)<=3: return name
    if len(words)>=2: return (words[0][0]+words[1][0]).upper()
    if len(caps)>=2: return caps[0]+caps[1]
    return name[:2]

# ---------- Skill glyphs ----------
# Generic line glyphs drawn for this site in the same stroke style as ICONS. They describe the kind of
# technology and are NOT official trademarks; an uploaded official icon (the CMS "icon" field) always wins.
_G='fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
_GT=_G.replace('1.6','1.35')  # thinner strokes for the small letterforms inside the hexagon
SKILL_GLYPHS={
 'network-switch':f'<rect x="3" y="13" width="18" height="7" rx="2" {_G}/><path d="M7 16.5h.01M10 16.5h.01M13 16.5h.01M16.5 16.5H18M12 13V9M6 13v-2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2" {_G}/><circle cx="12" cy="6" r="2.2" {_G}/>',
 'router':f'<rect x="3" y="13" width="18" height="7" rx="2" {_G}/><path d="M7 16.5h.01M10 16.5h.01M7 13l-1.5-5M17 13l1.5-5M14.5 16.5H18" {_G}/><path d="M9.5 6.2a4 4 0 0 1 5 0M7.8 4.2a6.6 6.6 0 0 1 8.4 0" {_G}/>',
 'packet-analyzer':f'<path d="M5 16.5c3.4-.6 6-3.9 7-11.5 1.6 5.4 3.8 9.4 7 11.5" {_G}/><path d="M2.5 20c1.6-1.3 3.2-1.3 4.8 0s3.2 1.3 4.8 0 3.2-1.3 4.8 0 3.2 1.3 4.6 0" {_G}/>',
 'containers':f'<rect x="3" y="12" width="5.5" height="4.5" rx="1" {_G}/><rect x="9.25" y="12" width="5.5" height="4.5" rx="1" {_G}/><rect x="15.5" y="12" width="5.5" height="4.5" rx="1" {_G}/><rect x="6.1" y="6.5" width="5.5" height="4.5" rx="1" {_G}/><rect x="12.4" y="6.5" width="5.5" height="4.5" rx="1" {_G}/><path d="M2.5 19.5h19" {_G}/>',
 'virtual-machines':f'<rect x="8" y="3" width="13" height="10" rx="2" {_G}/><rect x="3" y="9" width="13" height="10" rx="2" {_G}/><path d="M7 21h5M9.5 19v2" {_G}/>',
 'server':f'<rect x="4" y="3.5" width="16" height="7" rx="2" {_G}/><rect x="4" y="13.5" width="16" height="7" rx="2" {_G}/><path d="M7.5 7h.01M7.5 17h.01M11 7h5.5M11 17h5.5" {_G}/>',
 'database':f'<ellipse cx="12" cy="5.5" rx="7.5" ry="2.75" {_G}/><path d="M4.5 5.5v13c0 1.5 3.4 2.75 7.5 2.75s7.5-1.25 7.5-2.75v-13M4.5 12c0 1.5 3.4 2.75 7.5 2.75s7.5-1.25 7.5-2.75" {_G}/>',
 'code-cpp':f'<path d="M12 2.8 20 7.4v9.2L12 21.2 4 16.6V7.4z" {_G}/><path d="M11.2 9.4a3.2 3.2 0 1 0 0 5.2M14.8 10.6v2.8M13.4 12h2.8M18 10.6v2.8M16.6 12h2.8" {_GT}/>',
 'code-csharp':f'<path d="M12 2.8 20 7.4v9.2L12 21.2 4 16.6V7.4z" {_G}/><path d="M11.2 9.4a3.2 3.2 0 1 0 0 5.2M15 9.8l-.6 4.4M17.2 9.8l-.6 4.4M13.9 11h4.2M13.6 13h4.2" {_GT}/>',
 'mobile-app':f'<rect x="6" y="2.5" width="12" height="19" rx="2.5" {_G}/><path d="M10.5 18.5h3M13.8 6.8 9.6 11l4.2 4.2M11.9 13.3l1.9-1.9" {_G}/>',
 'terminal':f'<rect x="2.5" y="4" width="19" height="16" rx="2.5" {_G}/><path d="m6.5 9.5 3 2.5-3 2.5M12 15h5" {_G}/>',
 'web-stack':f'<path d="m12 3.5 8.5 4.25L12 12 3.5 7.75z" {_G}/><path d="m3.5 12 8.5 4.25L20.5 12M3.5 16.25 12 20.5l8.5-4.25" {_G}/>',
 'task-board':f'<rect x="3.5" y="3.5" width="17" height="17" rx="3" {_G}/><path d="m7.2 9 1.6 1.6L11.6 8M7.2 15l1.6 1.6 2.8-2.6M14 9.5h3.2M14 15.5h3.2" {_G}/>',
}

def skill_visual(s,large=False):
    """Uploaded official icon > built-in glyph > text monogram. Every option keeps a square, undistorted box."""
    size=40 if large else 28
    if s.get('icon'):
        return f'<img class="skill-logo" src="{E(media(s["icon"],IMG))}" alt="" width="{size}" height="{size}" loading="lazy" decoding="async">'
    key=s.get('icon_key') or ''
    if key:
        if key not in SKILL_GLYPHS: raise ValueError('Unknown built-in skill icon: '+str(key))
        return f'<svg class="skill-glyph" viewBox="0 0 24 24" width="{size}" height="{size}" aria-hidden="true" focusable="false">{SKILL_GLYPHS[key]}</svg>'
    return f'<span class="skill-monogram" aria-hidden="true">{E(monogram(s["name"]))}</span>'

def skill_icon_box(s,large=False):
    kind='logo' if s.get('icon') else ('glyph' if s.get('icon_key') else 'monogram')
    cls='skill-tile__icon skill-tile__icon--'+kind+(' skill-tile__icon--large' if large else '')
    return f'<span class="{cls}">{skill_visual(s,large)}</span>'

# ---------- Template helpers ----------
def fill(src,key,value_html):
    """Replace the inner HTML of every element marked data-field="key" and drop the marker."""
    pat=re.compile(r'(<(\w+)\b[^>]*?)\s+data-field="'+re.escape(key)+r'"([^>]*>)(.*?)(</\2>)',re.S)
    new,n=pat.subn(lambda m:m.group(1)+m.group(3)+value_html+m.group(5),src)
    if n==0: raise ValueError('Template field missing: '+key)
    return new

def slot(src,key,value_html):
    pat=re.compile(r'<!-- slot:'+re.escape(key)+r' -->.*?<!-- /slot:'+re.escape(key)+r' -->',re.S)
    new,n=pat.subn(lambda m:value_html,src)
    if n==0: raise ValueError('Template slot missing: '+key)
    return new

def section(title,content,cls=''):
    return f'<section class="detail-section {cls}"><h2>{E(title)}</h2>{content}</section>' if content else ''

def para(value):
    value=txt(value); return f'<p>{E(value)}</p>' if value else ''

def evidence(items):
    entries=[]
    for i in items or []:
        label=txt(i.get('label')) or 'Evidence'
        url=media(i.get('file'),DOC) if i.get('file') else valid_url(i.get('url'))
        if url: entries.append(f'<li><a href="{E(url)}">{E(label)}</a></li>')
    return section('Supporting evidence','<ul class="link-list">'+''.join(entries)+'</ul>') if entries else ''

def feature_list(items):
    entries=[]
    for entry in items or []:
        status=entry.get('status'); content=txt(entry.get('text'))
        if status not in STATUSES: raise ValueError('Feature or technology requires an explicit valid status')
        if content: entries.append(f'<li><span>{E(content)}</span><span class="status status--{status}">{STATUSES[status]}</span></li>')
    return section('Features','<ul class="feature-list">'+''.join(entries)+'</ul>') if entries else ''

def page(template,title,meta,body,profile):
    values={'TITLE':title+' | '+profile['name'],'META':meta or title,'NAME':profile['name']}
    for k,v in values.items(): template=template.replace('{{'+k+'}}',E(v))
    template=prefix_root_urls(template)
    return template.replace('{{BODY}}',body)

def check_output(text_value,where):
    if re.search('[\u0600-\u06FF]',text_value): raise ValueError('Non-English script found in '+where)
    for marker in ('data-field=','<!-- slot:','{{'):
        if marker in text_value: raise ValueError(f'Unfilled template marker {marker!r} in {where}')

def do_build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(); (OUT/'data').mkdir()
    for f in ('style.css','script.js'): shutil.copyfile(R/f,OUT/f)
    profile=read(R/'data/profile.json'); education=read(R/'data/education.json'); certs=read(R/'data/certificates.json')
    projects_all=records('projects'); skills_all=records('skills'); allskills={s['id']:s for s in skills_all}
    for p in projects_all:
        for ref in p.get('skills') or []:
            if ref not in allskills: raise ValueError('Unknown skill reference: '+str(ref))
    projects=[x for x in projects_all if x['status']=='published']; skills=[x for x in skills_all if x['status']=='published']; skillmap={s['id']:s for s in skills}
    for p in projects:
        for key in ('github_url','live_url','video_url'):
            if txt(p.get(key)) and not valid_url(txt(p.get(key))): raise ValueError(f'Invalid {key} (must start with https://) in project: '+p['id'])
        if p.get('live_verified') is True and not txt(p.get('live_url')): raise ValueError('Live demo is marked as checked but has no URL in project: '+p['id'])
    for kind,data in [('projects',projects),('skills',skills)]:
        # Clean output includes only published records and published relationships.
        safe=[]
        for item in data:
            c=dict(item)
            if kind=='projects':
                c['skills']=[v for v in c.get('skills',[]) if v in skillmap]
                if c.get('live_verified') is not True: c['live_url']=''
            safe.append(c)
        (OUT/'data'/f'{kind}.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

    display=txt(profile.get('name')); title=txt(profile.get('title')); intro=txt(profile.get('introduction'))
    email=txt(profile.get('email'))
    if not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+',email): raise ValueError('Invalid public email')
    linkedin=valid_url(profile.get('linkedin')); telegram=valid_url(profile.get('telegram')); github=valid_url(profile.get('github'))

    t=prefix_root_urls((R/'index.html').read_text(encoding='utf8'))
    t=re.sub(r'<title>.*?</title>',lambda m:'<title>'+E(display+' | '+title)+'</title>',t,count=1,flags=re.S)
    t=re.sub(r'<meta name="description" content="[^"]*">',lambda m:'<meta name="description" content="'+E(display+': '+intro)+'">',t,count=1)
    t=fill(t,'profile.name',E(display))
    # Hero: highlight the field of study inside the full title.
    role=E(title)
    if 'Information Technology' in title: role=role.replace('Information Technology','<span class="hero__field">Information Technology</span>',1)
    t=fill(t,'profile.title',role)
    parts=[E(x.strip()) for x in txt(profile.get('subtitle')).split('|') if x.strip()]
    t=fill(t,'profile.subtitle','<span class="hero__sep" aria-hidden="true">/</span>'.join(f'<span>{x}</span>' for x in parts))
    t=fill(t,'profile.introduction',E(intro))
    t=fill(t,'profile.biography',E(txt(profile.get('biography'))))
    t=fill(t,'profile.contact_message',E(txt(profile.get('contact_message'))))

    portrait=profile.get('profile_image')
    if portrait:
        uri=media(portrait,IMG)
        t=slot(t,'hero.portrait',f'<img src="{E(uri)}" alt="Portrait of {E(display)}" width="480" height="600" fetchpriority="high" decoding="async">')
        t=t.replace('class="hero__portrait"','class="hero__portrait has-photo"',1)
    else:
        t=slot(t,'hero.portrait','<div class="hero__placeholder" aria-hidden="true"><span>SA</span></div>')

    resume_button=''
    resume=profile.get('resume_pdf')
    if resume and profile.get('resume_verified') is True:
        # This is a sanity check, not a substitute for human review or a full PDF validator.
        resume_rel=str(resume).lstrip('/')
        if not resume_rel.startswith('media/') or '\\' in resume_rel or '..' in Path(resume_rel).parts: raise ValueError('Unsafe resume path')
        fp=(R/resume_rel).resolve()
        if not fp.is_relative_to((R/'media').resolve()): raise ValueError('Unsafe resume path')
        data=fp.read_bytes()
        if fp.suffix.lower()!='.pdf' or len(data)<128 or not data.startswith(b'%PDF-') or b'%%EOF' not in data[-2048:]: raise ValueError('Resume PDF failed basic integrity checks')
        url=media(resume,{'.pdf'})
        resume_button=f'<a class="button button--secondary" href="{E(url)}" download>{icon("download")}<span>Download Resume</span></a>'
    t=slot(t,'hero.resume',resume_button)

    # About: short editorial facts drawn only from existing data.
    facts=[('Degree',txt(education.get('degree'))),('University',txt(education.get('university'))),('Focus',txt(profile.get('subtitle')).replace(' | ',' · '))]
    t=slot(t,'about.facts',''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k,v in facts if v))

    featured=[p for p in projects if p.get('featured')]
    cards=''.join(project_card(p,feature=(i==0),index=i) for i,p in enumerate(featured))
    t=slot(t,'projects',cards)

    # Other Projects: published projects not shown as large cards, plus the GitHub profile button.
    # The section stays hidden when there is neither a GitHub URL nor a non-featured published project.
    others=[p for p in projects if not p.get('featured')]
    other=''
    if github or others:
        rows=''
        for p in others:
            gh=valid_url(p.get('github_url')); live=valid_url(p.get('live_url')) if p.get('live_verified') is True else ''
            extra=''.join(f'<a class="other-project__link" href="{E(u)}" rel="noopener noreferrer" target="_blank" aria-label="{E(txt(p["name"]))}: {lbl}">{icon(ic)}<span>{lbl}</span></a>' for u,ic,lbl in ((gh,'github','Repository'),(live,'external','Live Demo')) if u)
            summary=txt(p.get('summary'))
            rows+=(f'<li class="other-project"><a class="other-project__main" href="{E(details_url("projects",p))}"><span class="other-project__name">{E(txt(p["name"]))}</span>'
                   +(f'<span class="other-project__summary">{E(summary)}</span>' if summary else '')+'</a>'+('<span class="other-project__links">'+extra+'</span>' if extra else '')+'</li>')
        button=f'<a class="button button--primary" href="{E(github)}" rel="noopener noreferrer" target="_blank">{icon("github")}<span>Explore GitHub Projects</span></a>' if github else ''
        other=('<section class="other-projects" aria-labelledby="other-projects-title"><div class="container"><div class="other-projects__panel reveal">'
               '<div class="other-projects__head"><div><h2 id="other-projects-title">Other Projects</h2><p>Explore more of my experiments, practical work, and development projects.</p></div>'
               +button+'</div>'+(f'<ul class="other-projects__list">{rows}</ul>' if rows else '')+'</div></div></section>')
    t=slot(t,'other-projects',other)

    tiles=''.join(f'<li class="skill-tile reveal" style="--i:{i%8}"><a href="{E(details_url("skills",s))}">{skill_icon_box(s)}<span class="skill-tile__name">{E(s["name"])}</span></a></li>' for i,s in enumerate(skills))
    t=slot(t,'skills',tiles)

    t=fill(t,'education.university',E(txt(education.get('university'))))
    t=fill(t,'education.college',E(txt(education.get('college'))))
    t=fill(t,'education.degree',E(txt(education.get('degree'))))
    start=E(education.get('start_year')); end=E(education.get('expected_year'))
    years=f'{start} <span aria-hidden="true">&ndash;</span><span class="visually-hidden"> to </span> {end}'+('' if education.get('completed') is True else ' <span class="education-card__note">(Expected)</span>')
    t=fill(t,'education.years',years)
    desc=txt(education.get('description'))
    certlist=[]
    for c in certs:
        if c.get('status')!='published': continue
        label=txt(c.get('name')); url=media(c.get('file'),DOC) if c.get('file') else ''
        cert=f'<a href="{E(url)}">{E(label)}</a>' if url else E(label)
        verify=valid_url(c.get('verification_url'))
        meta=' · '.join(x for x in (E(txt(c.get('issuer'))),E(txt(c.get('issue_date')))) if x)
        certlist.append('<li><strong>'+cert+'</strong>'+(f' <span>{meta}</span>' if meta else '')+(f'<p>{E(txt(c.get("description")))}</p>' if txt(c.get('description')) else '')+(f' <a href="{E(verify)}" rel="noopener noreferrer">Verify certificate</a>' if verify else '')+'</li>')
    extra=(f'<p class="education-card__description">{E(desc)}</p>' if desc else '')+('<div class="certificates"><h3>Certificates</h3><ul>'+''.join(certlist)+'</ul></div>' if certlist else '')
    t=slot(t,'education.extra',extra)

    t=slot(t,'contact.action',f'<a class="button button--light" href="mailto:{E(email)}">{icon("mail")}<span>Reach out</span></a><a class="contact__email" href="mailto:{E(email)}">{E(email)}</a>')
    socials=[]
    if linkedin: socials.append(('LinkedIn','linkedin',linkedin))
    if github: socials.append(('GitHub','github',github))
    socials.append(('Email','mail','mailto:'+email))
    if telegram: socials.append(('Telegram','telegram',telegram))
    def social_html(cls):
        return ''.join(f'<li><a class="{cls}" href="{E(u)}" aria-label="{E(label)}"'+('' if u.startswith('mailto:') else ' rel="me noopener noreferrer" target="_blank"')+f'>{icon(ic)}</a></li>' for label,ic,u in socials)
    t=slot(t,'contact.social',social_html('social-icon'))
    t=slot(t,'footer.social',social_html('social-icon social-icon--small'))
    check_output(t,'index.html')
    (OUT/'index.html').write_text(t,encoding='utf8')

    pt=(R/'projects/index.html').read_text(encoding='utf8'); st=(R/'skills/index.html').read_text(encoding='utf8')
    for p in projects:
        name=txt(p['name']); full=txt(p.get('full_name')); summary=txt(p.get('summary'))
        links=project_links(p)
        body=(f'<a class="back-link" href="{E(site_path("/#portfolio"))}">'+icon('arrow-left')+'<span>Back to portfolio</span></a>'
              '<header class="detail-hero">'+(f'<div class="detail-hero__badges">{badges(p)}</div>' if badges(p) else '')+f'<h1>{E(name)}</h1>'
              +(f'<p class="detail-hero__sub">{E(full)}</p>' if full else '')+(f'<p class="detail-hero__lead">{E(summary)}</p>' if summary else '')
              +(f'<div class="detail-hero__actions">{links}</div>' if links else '')+'</header>')
        body+=f'<figure class="project-media project-media--{E(p["id"])} detail-cover">{project_media(p,eager=True)}</figure>'
        for key,label in [('overview','Overview'),('problem','Problem'),('objectives','Objectives'),('role','Role')]: body+=section(label,para(p.get(key)))
        body+=feature_list(p.get('features'))
        body+=section('Technologies',tech_block(p))
        imgs=''.join(f'<figure class="detail-media"><img src="{E(media(img,IMG))}" alt="{E(name)} project image" loading="lazy" decoding="async"></figure>' for img in p.get('images') or [])
        body+=section('Gallery',imgs)
        body+=evidence(p.get('evidence'))
        related=[skillmap[x] for x in p.get('skills',[]) if x in skillmap]
        if related: body+=section('Related skills','<ul class="tag-list">'+''.join(f'<li class="tag"><a href="{details_url("skills",s)}">{E(s["name"])}</a></li>' for s in related)+'</ul>')
        out=OUT/'projects'/p['slug']; out.mkdir(parents=True)
        html_out=page(pt,name,summary,body,profile); check_output(html_out,'project '+p['slug']); (out/'index.html').write_text(html_out,encoding='utf8')
    for s in skills:
        name=txt(s['name'])
        content=section('Description',para(s.get('description')))+section('Practical experience',para(s.get('experience')))+evidence(s.get('evidence'))
        related=[p for p in projects if s['id'] in (p.get('skills') or [])]
        if related: content+=section('Related projects','<ul class="link-list">'+''.join(f'<li><a href="{details_url("projects",p)}">{E(txt(p["name"]))}</a></li>' for p in related)+'</ul>')
        if not content: content='<p class="detail-empty">Details and supporting evidence for this skill will be added soon.</p>'
        body=(f'<a class="back-link" href="{E(site_path("/#skills"))}">'+icon('arrow-left')+'<span>Back to skills</span></a>'
              f'<header class="detail-hero detail-hero--skill">{skill_icon_box(s,large=True)}<h1>{E(name)}</h1></header>'+content)
        out=OUT/'skills'/s['slug']; out.mkdir(parents=True)
        html_out=page(st,name,txt(s.get('description')) or name,body,profile); check_output(html_out,'skill '+s['slug']); (out/'index.html').write_text(html_out,encoding='utf8')
    not_found='<!doctype html><html lang="en" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect width=%2232%22 height=%2232%22 rx=%229%22 fill=%22%231d3b5e%22/%3E%3Ctext x=%2216%22 y=%2221%22 font-family=%22Arial%22 font-size=%2212%22 font-weight=%22700%22 fill=%22white%22 text-anchor=%22middle%22%3ESA%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="/style.css"></head><body><main class="detail-shell not-found"><p class="not-found__code">404</p><h1>Page not found</h1><p>We could not find this page.</p><a class="button button--primary" href="/">Back to home</a></main></body></html>'
    (OUT/'404.html').write_text(prefix_root_urls(not_found),encoding='utf8')
    print(f'Built {len(projects)} published projects and {len(skills)} published skills to dist/.')

if __name__=='__main__':
    try: do_build()
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc: print('Build failed:',exc,file=sys.stderr); sys.exit(1)
