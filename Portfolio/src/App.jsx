import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion, useScroll, useSpring, useTransform } from 'framer-motion';
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUp,
  Braces,
  Check,
  ChevronDown,
  Circle,
  Code2,
  Command,
  Database,
  ExternalLink,
  Layers3,
  Mail,
  Menu,
  MousePointer2,
  Send,
  Sparkles,
  Terminal as TerminalIcon,
  X,
} from 'lucide-react';
import { profile, roles, skillGroups, skills } from './data/profile.js';
import { projects } from './data/projects.js';

const navItems = [
  ['About', 'about'],
  ['Toolkit', 'skills'],
  ['Projects', 'projects'],
  ['Journey', 'journey'],
  ['Contact', 'contact'],
];

const highlights = [
  { number: '01', title: 'BCA graduate', detail: 'A foundation in computer applications and software.' },
  { number: '02', title: 'Python full stack intern', detail: 'Hands-on development experience at Synnefo Solutions.' },
  { number: '03', title: 'Project focused', detail: 'Building practical applications to grow through hands-on work.' },
  { number: '04', title: 'Open to opportunities', detail: 'Entry-level software and IT roles, remote, hybrid, or on-site.' },
];

const capabilities = [
  { icon: Braces, title: 'Python & Django', text: 'Build the server-side logic, views, and data flows that bring a web application together.' },
  { icon: Code2, title: 'Backend & REST APIs', text: 'Connect interface needs to backend routes and API responses with clear, useful data flows.' },
  { icon: Layers3, title: 'Responsive frontend', text: 'Create layouts that feel considered across desktop, tablet, and mobile.' },
  { icon: Braces, title: 'React interfaces', text: 'Compose reusable components and add interaction where it helps people move through a product.' },
  { icon: Database, title: 'Database-driven apps', text: 'Work with structured and document data to make application features useful.' },
  { icon: Sparkles, title: 'UI/UX awareness', text: 'Pay attention to clear flows, visual hierarchy, and the details that make a page easier to use.' },
  { icon: ArrowRight, title: 'Learning & problem-solving', text: 'Break new challenges into steps, ask good questions, and keep improving through practice.' },
];

const terminalCommands = ['whoami', 'skills', 'projects', 'contact', 'help'];

function GitHubMark({ size = 16 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .75a11.25 11.25 0 0 0-3.56 21.92c.56.1.77-.24.77-.54v-2.05c-3.14.69-3.8-1.34-3.8-1.34-.51-1.31-1.26-1.66-1.26-1.66-1.03-.7.08-.69.08-.69 1.14.08 1.74 1.17 1.74 1.17 1.01 1.73 2.65 1.23 3.3.94.1-.73.4-1.23.72-1.51-2.51-.29-5.15-1.26-5.15-5.6 0-1.24.44-2.25 1.17-3.05-.12-.29-.51-1.44.11-3 0 0 .95-.3 3.11 1.16a10.8 10.8 0 0 1 5.66 0c2.16-1.46 3.1-1.16 3.1-1.16.63 1.56.24 2.71.12 3 .73.8 1.17 1.81 1.17 3.05 0 4.35-2.65 5.3-5.17 5.58.41.35.77 1.04.77 2.1v3.12c0 .3.2.65.78.54A11.25 11.25 0 0 0 12 .75Z" /></svg>;
}

function Reveal({ children, className = '', delay = 0 }) {
  const reduceMotion = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduceMotion ? false : { opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.14 }}
      transition={{ duration: reduceMotion ? 0 : 0.65, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

function CanvasField() {
  const canvasRef = useRef(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx || reduceMotion) return undefined;

    let width = 0;
    let height = 0;
    let frame = 0;
    let visible = true;
    const pointer = { x: -1000, y: -1000 };
    const parent = canvas.parentElement;
    const resize = () => {
      const rect = parent.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const move = (event) => {
      const rect = canvas.getBoundingClientRect();
      pointer.x = event.clientX - rect.left;
      pointer.y = event.clientY - rect.top;
    };
    resize();
    window.addEventListener('resize', resize, { passive: true });
    parent.addEventListener('pointermove', move, { passive: true });
    const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; });
    observer.observe(parent);

    const amount = width < 640 ? 27 : 54;
    const nodes = Array.from({ length: amount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.16,
      vy: (Math.random() - 0.5) * 0.16,
      r: Math.random() * 1.3 + 0.6,
    }));
    const draw = () => {
      frame = requestAnimationFrame(draw);
      if (!visible) return;
      ctx.clearRect(0, 0, width, height);
      nodes.forEach((node, index) => {
        const dx = pointer.x - node.x;
        const dy = pointer.y - node.y;
        const distance = Math.hypot(dx, dy);
        if (distance < 140 && distance > 0) {
          node.vx -= (dx / distance) * 0.002;
          node.vy -= (dy / distance) * 0.002;
        }
        node.vx = Math.max(-0.35, Math.min(0.35, node.vx * 0.997));
        node.vy = Math.max(-0.35, Math.min(0.35, node.vy * 0.997));
        node.x += node.vx;
        node.y += node.vy;
        if (node.x < -5) node.x = width + 5;
        if (node.x > width + 5) node.x = -5;
        if (node.y < -5) node.y = height + 5;
        if (node.y > height + 5) node.y = -5;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
        ctx.fillStyle = index % 5 === 0 ? 'rgba(139, 92, 246, .62)' : 'rgba(0, 245, 212, .5)';
        ctx.fill();
        for (let next = index + 1; next < nodes.length; next += 1) {
          const other = nodes[next];
          const gap = Math.hypot(other.x - node.x, other.y - node.y);
          if (gap < 100) {
            ctx.beginPath();
            ctx.moveTo(node.x, node.y);
            ctx.lineTo(other.x, other.y);
            ctx.strokeStyle = `rgba(91, 116, 157, ${0.12 * (1 - gap / 100)})`;
            ctx.lineWidth = 0.7;
            ctx.stroke();
          }
        }
      });
    };
    draw();
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('resize', resize);
      parent.removeEventListener('pointermove', move);
      observer.disconnect();
    };
  }, [reduceMotion]);

  return <canvas ref={canvasRef} className="particle-canvas" aria-hidden="true" />;
}

function CustomCursor() {
  const dotRef = useRef(null);
  const ringRef = useRef(null);
  const labelRef = useRef(null);

  useEffect(() => {
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!finePointer || reduced) return undefined;

    document.body.classList.add('has-custom-cursor');
    let x = -100;
    let y = -100;
    let ringX = x;
    let ringY = y;
    let frame = 0;
    const move = (event) => {
      x = event.clientX;
      y = event.clientY;
      const target = event.target instanceof Element ? event.target.closest('[data-cursor]') : null;
      const text = target?.getAttribute('data-cursor') || '';
      labelRef.current.textContent = text;
      ringRef.current.classList.toggle('is-active', Boolean(target));
    };
    const animate = () => {
      ringX += (x - ringX) * 0.15;
      ringY += (y - ringY) * 0.15;
      dotRef.current.style.transform = `translate3d(${x}px, ${y}px, 0)`;
      ringRef.current.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
      frame = requestAnimationFrame(animate);
    };
    window.addEventListener('pointermove', move, { passive: true });
    frame = requestAnimationFrame(animate);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('pointermove', move);
      document.body.classList.remove('has-custom-cursor');
    };
  }, []);

  return (
    <div className="custom-cursor" aria-hidden="true">
      <span ref={dotRef} className="cursor-dot" />
      <span ref={ringRef} className="cursor-ring"><span ref={labelRef} /></span>
    </div>
  );
}

function PortraitFeature() {
  const stageRef = useRef(null);
  const cardRef = useRef(null);
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: stageRef, offset: ['start end', 'end start'] });
  const parallaxY = useTransform(scrollYProgress, [0, 1], [16, -16]);

  const tilt = (event) => {
    if (reduceMotion || event.pointerType === 'touch' || !cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;
    cardRef.current.style.setProperty('--portrait-rx', `${(0.5 - py) * 4}deg`);
    cardRef.current.style.setProperty('--portrait-ry', `${(px - 0.5) * 7}deg`);
  };

  const resetTilt = () => {
    if (!cardRef.current) return;
    cardRef.current.style.setProperty('--portrait-rx', '0deg');
    cardRef.current.style.setProperty('--portrait-ry', '0deg');
  };

  return (
    <motion.div ref={stageRef} className="portrait-stage" style={{ y: reduceMotion ? 0 : parallaxY }} aria-label="Portrait of Swetha Biju">
      <div ref={cardRef} className="portrait-card" onPointerMove={tilt} onPointerLeave={resetTilt} data-cursor="3D VIEW">
        <img src="/swetha-biju-portrait.webp" alt="Swetha Biju, Python Full Stack Developer" fetchPriority="high" />
      </div>
      <div className="portrait-nameplate"><span className="availability-dot" /><span className="portrait-nameplate-copy"><b>Swetha Biju</b><small>PYTHON FULL STACK DEVELOPER</small></span><strong>SB<span>.</span></strong></div>
    </motion.div>
  );
}

function MagneticLink({ href, children, className = '', ...props }) {
  const ref = useRef(null);
  const reduceMotion = useReducedMotion();
  const onMove = (event) => {
    if (reduceMotion || event.pointerType === 'touch') return;
    const rect = ref.current.getBoundingClientRect();
    const dx = event.clientX - rect.left - rect.width / 2;
    const dy = event.clientY - rect.top - rect.height / 2;
    ref.current.style.setProperty('--mx', `${dx * 0.14}px`);
    ref.current.style.setProperty('--my', `${dy * 0.14}px`);
  };
  const reset = () => {
    ref.current?.style.setProperty('--mx', '0px');
    ref.current?.style.setProperty('--my', '0px');
  };
  return (
    <a ref={ref} href={href} className={`magnetic-link ${className}`} onPointerMove={onMove} onPointerLeave={reset} data-cursor="GO" {...props}>
      {children}
    </a>
  );
}

function SectionHeading({ eyebrow, title, note, index }) {
  return (
    <div className="section-heading">
      <div>
        <p className="eyebrow"><span>{index}</span>{eyebrow}</p>
        <h2>{title}</h2>
      </div>
      {note && <p className="section-note">{note}</p>}
    </div>
  );
}

function ProjectPreview({ project }) {
  if (project.image) {
    return <div className="preview-shell preview-image"><img src={project.image} alt={`${project.name} project screenshot`} loading="lazy" /><span className="preview-watermark">PROJECT SCREENSHOT</span></div>;
  }
  if (project.visual === 'console') {
    return (
      <div className="preview-shell preview-console" aria-label="Concept preview, not an application screenshot">
        <div className="preview-topbar"><span className="preview-brand"><span className="brand-mark brand-mark--small">O</span> opsmind</span><span className="preview-pill"><Circle size={6} fill="currentColor" /> SYSTEM ONLINE</span></div>
        <div className="preview-console-body">
          <div className="preview-side"><span className="side-active"><Layers3 size={13} /> Overview</span><span><Database size={13} /> Knowledge</span><span><TerminalIcon size={13} /> Console</span></div>
          <div className="preview-main"><div className="preview-label">WORKSPACE / OVERVIEW</div><div className="preview-title">Good morning, operator<span>.</span></div><div className="preview-metrics"><div><small>Signals indexed</small><b>1,284</b><i>+12.8%</i></div><div><small>Response quality</small><b>98.6<span>%</span></b><i>stable</i></div></div><div className="preview-query"><span className="query-spark"><Sparkles size={13} /></span><span>Ask your workspace anything…</span><ArrowRight size={14} /></div></div>
        </div>
        <span className="preview-watermark">CONCEPT UI</span>
      </div>
    );
  }
  if (project.visual === 'recipe') {
    return (
      <div className="preview-shell preview-recipe" aria-label="Concept preview, not an application screenshot">
        <div className="recipe-glow" />
        <div className="recipe-nav"><span>recipe<span className="recipe-dot">.</span>sense</span><span>DISCOVER&nbsp;&nbsp; COLLECTIONS</span><span className="recipe-avatar">S</span></div>
        <div className="recipe-content"><span className="recipe-kicker">A LITTLE INSPIRATION</span><b>Something good<br />is cooking.</b><span className="recipe-search">⌕ &nbsp; What are you craving today?</span><div className="recipe-chips"><span>Quick & easy</span><span>Fresh picks</span><span>Comfort food</span></div></div>
        <div className="recipe-dish dish-one">🥗<small>01</small></div><div className="recipe-dish dish-two">🍝<small>02</small></div><span className="preview-watermark">CONCEPT UI</span>
      </div>
    );
  }
  return (
    <div className="preview-shell preview-gallery" aria-label="Concept preview, not an application screenshot">
      <div className="gallery-top"><span><span className="gallery-mark">G</span> Gallery Vault</span><span>COLLECTION / 08</span><span className="gallery-menu">•••</span></div>
      <div className="gallery-layout"><div className="gallery-heading"><span>CURATED MOMENTS</span><b>Keep the<br />good things.</b><small>VIEW COLLECTION <ArrowRight size={11} /></small></div><div className="gallery-tiles"><div className="gallery-tile tile-a"><span>01</span><i /></div><div className="gallery-tile tile-b"><span>02</span><i /></div><div className="gallery-tile tile-c"><span>03</span><i /></div></div></div>
      <span className="preview-watermark">CONCEPT UI</span>
    </div>
  );
}

function ProjectCard({ project, delay }) {
  const ref = useRef(null);
  const reduceMotion = useReducedMotion();
  const onMove = (event) => {
    if (reduceMotion || event.pointerType === 'touch') return;
    const rect = ref.current.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;
    ref.current.style.setProperty('--rx', `${(0.5 - py) * 3}deg`);
    ref.current.style.setProperty('--ry', `${(px - 0.5) * 4}deg`);
    ref.current.style.setProperty('--glow-x', `${px * 100}%`);
    ref.current.style.setProperty('--glow-y', `${py * 100}%`);
  };
  const reset = () => {
    if (!ref.current) return;
    ref.current.style.setProperty('--rx', '0deg');
    ref.current.style.setProperty('--ry', '0deg');
    ref.current.style.setProperty('--glow-x', '50%');
    ref.current.style.setProperty('--glow-y', '50%');
  };
  return (
    <Reveal className={`project-card-wrap ${project.featured ? 'project-card-wrap--featured' : ''}`} delay={delay}>
      <article ref={ref} className={`project-card project-card--${project.tone}`} onPointerMove={onMove} onPointerLeave={reset}>
        <ProjectPreview project={project} />
        <div className="project-copy">
          <div className="project-meta"><span>{project.number} / FEATURED PROJECT</span><span>{project.category}</span></div>
          <h3>{project.name}<span className="project-period">.</span></h3>
          <p>{project.summary}</p>
          <div className="tech-list">{project.tech.map((item) => <span key={item}>{item}</span>)}</div>
          <div className="project-actions">
            {project.repository ? (
              <a href={project.repository} target="_blank" rel="noreferrer" className="text-link" data-cursor="VIEW"><GitHubMark size={15} /> Source code <ExternalLink size={12} /></a>
            ) : (
              <span className="link-pending">Repository URL to add</span>
            )}
            {project.demo && <a href={project.demo} target="_blank" rel="noreferrer" className="text-link" data-cursor="VIEW">Live demo <ExternalLink size={12} /></a>}
            <details className="project-details"><summary>Project notes <ChevronDown size={14} /></summary><p>{project.details}</p></details>
          </div>
        </div>
      </article>
    </Reveal>
  );
}

function TerminalPanel({ onEasterEgg }) {
  const [command, setCommand] = useState('');
  const [history, setHistory] = useState([
    { command: '', output: 'A small, safe portfolio terminal. Choose a command or type one below.' },
  ]);
  const run = (raw) => {
    const value = raw.trim().toLowerCase();
    if (!value) return;
    let output = '';
    switch (value) {
      case 'whoami':
        output = 'Swetha Biju — BCA graduate and Python Full Stack developer in Kerala, India. Fresher, open to entry-level IT opportunities.';
        break;
      case 'skills':
        output = 'Python · Django · Flask · JavaScript · React.js · HTML · CSS · REST APIs · SQL · SQLite · MongoDB · Git';
        break;
      case 'projects':
        output = projects.map((project) => `${project.number}  ${project.name} — ${project.category}`).join('\n');
        break;
      case 'contact':
        output = `GitHub: ${profile.githubUrl}\nEmail: ${profile.email || 'Add your professional email in src/data/profile.js'}\nLinkedIn: ${profile.linkedinUrl || 'Add your LinkedIn URL in src/data/profile.js'}`;
        break;
      case 'help':
        output = `Available commands: ${terminalCommands.join(' · ')}\nType a command and press Enter.`;
        break;
      case 'theme':
        onEasterEgg();
        output = 'Violet afterglow toggled. A little hidden color for the curious.';
        break;
      default:
        output = `Command not found: ${value}. Try "help" for the safe command list.`;
    }
    setHistory((previous) => [...previous.slice(-6), { command: value, output }]);
    setCommand('');
  };
  return (
    <div className="terminal-window">
      <div className="terminal-topbar"><div className="traffic-lights"><i /><i /><i /></div><span><TerminalIcon size={13} /> swetha@portfolio: ~</span><span className="terminal-status">LOCAL SESSION</span></div>
      <div className="terminal-output" aria-live="polite" aria-label="Terminal output">
        {history.map((entry, index) => (
          <div className="terminal-entry" key={`${entry.command}-${index}`}>
            {entry.command && <div className="terminal-command"><span>swetha@portfolio:~$</span> {entry.command}</div>}
            <p>{entry.output.split('\n').map((line, lineIndex) => <span key={lineIndex}>{lineIndex > 0 && <br />}{line}</span>)}</p>
          </div>
        ))}
      </div>
      <form className="terminal-input-row" onSubmit={(event) => { event.preventDefault(); run(command); }}>
        <label htmlFor="terminal-command"><span>swetha@portfolio:~$</span><span className="sr-only">Enter a portfolio terminal command</span></label>
        <input id="terminal-command" value={command} onChange={(event) => setCommand(event.target.value)} autoComplete="off" spellCheck="false" aria-describedby="terminal-hint" />
        <span className="terminal-caret" aria-hidden="true" />
      </form>
      <div className="terminal-suggestions" id="terminal-hint"><span>TRY</span>{terminalCommands.map((item) => <button type="button" key={item} onClick={() => run(item)}>{item}</button>)}</div>
      <span className="terminal-easter-egg" aria-hidden="true">a curious developer might try: theme</span>
    </div>
  );
}

function ContactForm() {
  const [state, setState] = useState('idle');
  const endpoint = `https://formsubmit.co/ajax/${profile.email}`;
  const submit = async (event) => {
    event.preventDefault();
    setState('sending');
    const form = event.currentTarget;
    const fields = Object.fromEntries(new FormData(form).entries());
    const payload = { ...fields, _subject: `Portfolio message: ${fields.subject}` };
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('The message service returned an error.');
      const result = await response.json().catch(() => null);
      if (result?.success === false || result?.success === 'false') throw new Error('The message service rejected the message.');
      form.reset();
      setState('sent');
    } catch {
      setState('error');
    }
  };
  return (
    <form className="contact-form" onSubmit={submit}>
      <div className="form-grid">
        <label>Your name<input name="name" type="text" placeholder="Ada Lovelace" autoComplete="name" required /></label>
        <label>Your email<input name="email" type="email" placeholder="you@example.com" autoComplete="email" required /></label>
      </div>
      <label>Subject<input name="subject" type="text" placeholder="A little about the opportunity" maxLength="140" required /></label>
      <label>Your message<textarea name="message" rows="4" placeholder="Tell me what you have in mind…" maxLength="5000" required /></label>
      <div className="form-bottom">
        <p className={`form-feedback form-feedback--${state}`} aria-live="polite">
          {state === 'sending' && 'Sending your message…'}
          {state === 'sent' && 'Message submitted. Thank you for reaching out.'}
          {state === 'error' && 'The message could not be sent. Please check the endpoint or try again later.'}
          {state === 'idle' && 'Messages are delivered to Swetha’s inbox through FormSubmit.'}
        </p>
        <button className="button button--primary form-submit" type="submit" disabled={state === 'sending'} data-cursor="SEND">
          {state === 'sending' ? 'Sending' : state === 'sent' ? 'Sent' : 'Send a message'} {state === 'sent' ? <Check size={16} /> : <Send size={15} />}
        </button>
      </div>
    </form>
  );
}

function App() {
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const progress = useSpring(scrollYProgress, { stiffness: 100, damping: 30, restDelta: 0.001 });
  const [roleText, setRoleText] = useState(roles[0]);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('home');
  const [scrolled, setScrolled] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(skills[0]);
  const [violetMode, setVioletMode] = useState(false);
  const year = new Date().getFullYear();

  useEffect(() => {
    if (reduceMotion) return undefined;
    let roleIndex = 0;
    let charIndex = roles[0].length;
    let deleting = false;
    let timeout;
    const tick = () => {
      const current = roles[roleIndex];
      charIndex += deleting ? -1 : 1;
      setRoleText(current.slice(0, Math.max(charIndex, 0)));
      let delay = deleting ? 28 : 54;
      if (!deleting && charIndex >= current.length) {
        deleting = true;
        delay = 1150;
      } else if (deleting && charIndex <= 0) {
        deleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        delay = 150;
      }
      timeout = window.setTimeout(tick, delay);
    };
    timeout = window.setTimeout(tick, 1300);
    return () => window.clearTimeout(timeout);
  }, [reduceMotion]);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 18);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    const sections = [...document.querySelectorAll('main section[id]')];
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) setActiveSection(visible.target.id);
    }, { rootMargin: '-22% 0px -65% 0px', threshold: [0, 0.15, 0.4] });
    sections.forEach((section) => observer.observe(section));
    return () => {
      window.removeEventListener('scroll', handleScroll);
      observer.disconnect();
    };
  }, []);

  const toggleTheme = () => setVioletMode((value) => !value);
  const closeMenu = () => setMobileOpen(false);
  const resumeReady = Boolean(profile.resumePath);
  const linkedinReady = Boolean(profile.linkedinUrl);

  return (
    <div className={`site-shell ${violetMode ? 'site-shell--violet' : ''}`}>
      <motion.div className="scroll-progress" style={{ scaleX: progress }} />
      <CustomCursor />
      <header className={`site-header ${scrolled ? 'site-header--scrolled' : ''}`}>
        <a className="wordmark" href="#home" aria-label="Swetha Biju, back to top" onClick={closeMenu} data-cursor="HOME">
          <span className="wordmark-symbol">S<span>.</span></span><span className="wordmark-name">SWETHA BIJU</span>
        </a>
        <nav className="desktop-nav" aria-label="Main navigation">
          {navItems.map(([label, id]) => <a key={id} href={`#${id}`} className={activeSection === id ? 'is-active' : ''} data-cursor="GO">{label}</a>)}
        </nav>
        <a className="header-contact" href="#contact" data-cursor="HELLO">Let’s talk <ArrowDownRight size={15} /></a>
        <button className="menu-toggle" type="button" aria-label={mobileOpen ? 'Close navigation menu' : 'Open navigation menu'} aria-expanded={mobileOpen} aria-controls="mobile-navigation" onClick={() => setMobileOpen((open) => !open)}>
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <AnimatePresence>
          {mobileOpen && <motion.nav id="mobile-navigation" className="mobile-nav" aria-label="Mobile navigation" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.18 }}>
            {navItems.map(([label, id], index) => <a key={id} href={`#${id}`} onClick={closeMenu} className={activeSection === id ? 'is-active' : ''}><span>0{index + 1}</span>{label}<ArrowDownRight size={14} /></a>)}
          </motion.nav>}
        </AnimatePresence>
      </header>

      <main>
        <section className="hero-section" id="home">
          <div className="hero-grid" aria-hidden="true" />
          <div className="hero-orb hero-orb--cyan" aria-hidden="true" />
          <div className="hero-orb hero-orb--violet" aria-hidden="true" />
          <CanvasField />
          <div className="container hero-container">
            <div className="hero-copy">
              <motion.div className="availability" initial={reduceMotion ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
                <span className="availability-dot" /><span>OPEN TO IT OPPORTUNITIES</span><span className="availability-line" />
              </motion.div>
              <motion.p className="hero-intro" initial={reduceMotion ? false : { opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55, delay: 0.08 }}>Hey, I’m <span>Swetha Biju.</span></motion.p>
              <motion.h1 initial={reduceMotion ? false : { opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.72, delay: 0.16, ease: [0.22, 1, 0.36, 1] }}>
                Building<br /><span className="headline-accent">digital</span> experiences<span className="headline-period">.</span>
              </motion.h1>
              <motion.div className="hero-role" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.32 }}>
                <span className="role-dash" /><span className="role-text" aria-live="off">{roleText}</span><span className="role-caret" aria-hidden="true" />
              </motion.div>
              <motion.p className="hero-tagline" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>One line of code at a time.</motion.p>
              <motion.p className="hero-description" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.46 }}>
                I’m a BCA graduate who loves turning ideas into useful web experiences with clean code, thoughtful design, and plenty of curiosity.
              </motion.p>
              <motion.div className="hero-actions" initial={reduceMotion ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.5 }}>
                <MagneticLink href="#projects" className="button button--primary">Explore my work <ArrowRight size={16} /></MagneticLink>
                {resumeReady ? <MagneticLink href={profile.resumePath} className="button button--ghost" download>Download resume <ArrowDownRight size={15} /></MagneticLink> : <button className="button button--ghost button--resume-disabled" type="button" disabled aria-describedby="resume-note">Resume PDF coming soon <ArrowDownRight size={15} /></button>}
                <a href="#contact" className="button button--text" data-cursor="HELLO">Let’s connect <ArrowDownRight size={16} /></a>
              </motion.div>
              {!resumeReady && <p className="resume-note" id="resume-note">Add your PDF at <code>public/Swetha-Biju-Resume.pdf</code> to enable download.</p>}
              <motion.div className="hero-socials" initial={reduceMotion ? false : { opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.72 }}>
                <a href={profile.githubUrl} target="_blank" rel="noreferrer" aria-label="Swetha's GitHub profile" data-cursor="OPEN"><GitHubMark size={17} /><span>GitHub</span><ExternalLink size={11} /></a>
                <span className="social-divider" />
                {linkedinReady ? <a href={profile.linkedinUrl} target="_blank" rel="noreferrer" aria-label="Swetha's LinkedIn profile" data-cursor="OPEN"><span className="linkedin-mark">in</span><span>LinkedIn</span><ExternalLink size={11} /></a> : <span className="social-pending"><span className="linkedin-mark">in</span><span>LinkedIn URL pending</span></span>}
                <span className="hero-location"><span className="location-pin" /> KERALA, INDIA</span>
              </motion.div>
            </div>
            <motion.div className="hero-art" initial={reduceMotion ? false : { opacity: 0, scale: 0.94, y: 16 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: 0.8, delay: 0.28, ease: [0.22, 1, 0.36, 1] }}>
              <PortraitFeature />
            </motion.div>
          </div>
          <div className="hero-bottom"><div className="container hero-bottom-inner"><span>SCROLL TO EXPLORE</span><a href="#about" aria-label="Scroll to About" data-cursor="DOWN"><span className="scroll-line" /><ArrowDownRight size={14} /></a><span className="hero-bottom-right">PORTFOLIO — 2026</span></div></div>
        </section>

        <section className="about-section section-pad" id="about">
          <div className="container">
            <Reveal><SectionHeading index="01" eyebrow="THE PERSON BEHIND THE PIXELS" title={<>A little about the human<br className="desktop-break" /> behind the code<span className="mint-period">.</span></>} note="Curious by nature. Building with intent." /></Reveal>
            <div className="about-layout">
              <Reveal className="about-story">
                <p className="about-lead">I’m a BCA graduate and Python Full Stack developer at the start of my professional journey.</p>
                <p>I completed Python Full Stack Development training at Synnefo Solutions. I enjoy connecting a thoughtful frontend with useful backend behavior, working with data, and exploring the details that make an interface feel right.</p>
                <p>Right now, I’m building practical projects to strengthen my skills and looking for an opportunity to begin my IT career with a team that likes learning and making things that matter.</p>
                <div className="about-signoff"><span className="signoff-line" /><span>Currently learning. Always building.</span></div>
              </Reveal>
              <Reveal className="terminal-wrap" delay={0.12}><TerminalPanel onEasterEgg={toggleTheme} /></Reveal>
            </div>
            <Reveal className="highlights-grid" delay={0.08}>
              {highlights.map((item) => <div className="highlight-item" key={item.number}><span className="highlight-number">{item.number}</span><div><h3>{item.title}</h3><p>{item.detail}</p></div><span className="highlight-arrow"><ArrowDownRight size={15} /></span></div>)}
            </Reveal>
          </div>
        </section>

        <section className="skills-section section-pad" id="skills">
          <div className="container">
            <Reveal><SectionHeading index="02" eyebrow="THE TOOLS I REACH FOR" title={<>My current<br className="mobile-break" /> toolkit<span className="mint-period">.</span></>} note="Growing one project at a time." /></Reveal>
            <div className="skills-layout">
              <Reveal className="constellation-panel">
                <div className="constellation-header"><span><Command size={14} /> INTERACTIVE SKILL MAP</span><span>SELECT A NODE <MousePointer2 size={12} /></span></div>
                <div className="constellation-field">
                  <svg className="constellation-lines" viewBox="0 0 620 390" preserveAspectRatio="none" aria-hidden="true"><path d="M85 125 210 80 330 144 470 86 540 176 413 247 265 220 135 295 85 125M210 80 265 220 330 144 413 247M470 86 413 247M135 295 265 220" /></svg>
                  {skills.map((skill, index) => <button key={skill.name} type="button" className={`skill-node skill-node--${index % 4} ${selectedSkill.name === skill.name ? 'is-selected' : ''}`} style={{ '--node': index }} onClick={() => setSelectedSkill(skill)} onMouseEnter={() => setSelectedSkill(skill)} onFocus={() => setSelectedSkill(skill)} aria-pressed={selectedSkill.name === skill.name} data-cursor="SELECT"><span className="node-dot" />{skill.name}</button>)}
                </div>
                <div className="skill-explainer" aria-live="polite"><span className="skill-explainer-mark"><Sparkles size={15} /></span><div><span className="skill-explainer-label">A LITTLE ABOUT THIS ONE</span><p><strong>{selectedSkill.name}.</strong> {selectedSkill.detail}</p></div><span className="skill-explainer-index">{String(skills.indexOf(selectedSkill) + 1).padStart(2, '0')} / {String(skills.length).padStart(2, '0')}</span></div>
              </Reveal>
              <Reveal className="skill-categories" delay={0.12}>
                <p className="category-intro">A toolkit in progress, shaped by training and hands-on exploration.</p>
                {skillGroups.map((group, index) => <div className="skill-group" key={group.name}><div className="skill-group-label"><span>0{index + 1}</span>{group.name}</div><div className="skill-badges">{group.skills.map((item) => <button key={item} type="button" onClick={() => { const found = skills.find((skill) => skill.name === item); if (found) setSelectedSkill(found); }} className={selectedSkill.name === item ? 'is-selected' : ''}>{item}<ArrowDownRight size={11} /></button>)}</div></div>)}
              </Reveal>
            </div>
          </div>
        </section>

        <section className="projects-section section-pad" id="projects">
          <div className="container">
            <Reveal><SectionHeading index="03" eyebrow="SELECTED WORK · THREE PROJECTS" title={<>Ideas made<br className="mobile-break" /> tangible<span className="mint-period">.</span></>} note="Small steps, real things built." /></Reveal>
            <div className="projects-intro"><p>Each project is a chance to learn by making. These previews are original concept visuals while real screenshots are unavailable.</p><span><span className="preview-legend-dot" /> CONCEPT PREVIEWS</span></div>
            <div className="projects-grid">{projects.map((project, index) => <ProjectCard key={project.name} project={project} delay={index * 0.08} />)}</div>
          </div>
        </section>

        <section className="capabilities-section section-pad" id="capabilities">
          <div className="container">
            <Reveal><SectionHeading index="04" eyebrow="HOW I LIKE TO CONTRIBUTE" title={<>More than just<br className="mobile-break" /> writing code<span className="mint-period">.</span></>} note="Useful, thoughtful, ready to learn." /></Reveal>
            <div className="capabilities-grid">
              {capabilities.map(({ icon: Icon, title, text }, index) => <Reveal key={title} delay={index * 0.07}><article className="capability-card"><span className="capability-index">0{index + 1}</span><span className="capability-icon"><Icon size={18} strokeWidth={1.7} /></span><h3>{title}</h3><p>{text}</p><span className="capability-arrow"><ArrowDownRight size={15} /></span></article></Reveal>)}
            </div>
            <div className="capability-note"><span className="note-sparkle"><Sparkles size={15} /></span><p>I’m early in my career, and I bring curiosity, care, and a willingness to grow into every new problem.</p></div>
          </div>
        </section>

        <section className="journey-section section-pad" id="journey">
          <div className="container">
            <Reveal><SectionHeading index="05" eyebrow="WHERE THE JOURNEY STARTED" title={<>Learning by<br className="mobile-break" /> doing<span className="mint-period">.</span></>} note="A foundation to keep building on." /></Reveal>
            <div className="journey-layout">
              <Reveal className="journey-intro"><p className="journey-statement">Every next step starts with what you choose to learn today.</p><span className="journey-location"><span className="location-pin" /> KERALA, INDIA <span className="journey-separator">/</span> OPEN TO REMOTE, HYBRID & ON-SITE</span></Reveal>
              <div className="timeline">
                <Reveal><article className="timeline-item"><span className="timeline-dot" /><div className="timeline-label"><span>PROFESSIONAL EXPERIENCE</span><span>JAN 2025 — FEB 2026</span></div><h3>Python Full Stack Development Intern</h3><p>At <strong>Synnefo Solutions</strong>, developing client-facing and internal applications with Python and Django and collaborating with design and QA teams.</p><span className="timeline-foot">PYTHON · DJANGO · FRONTEND · DATABASES</span></article></Reveal>
                <Reveal delay={0.12}><article className="timeline-item"><span className="timeline-dot timeline-dot--violet" /><div className="timeline-label"><span>EDUCATION</span><span>GRADUATED JAN 2025</span></div><h3>Bachelor of Computer Applications <span>(BCA)</span></h3><p>Completed at <strong>BVM Holy Cross College, Cherpunkal</strong>.</p><span className="timeline-foot">COMPUTER APPLICATIONS · KERALA, INDIA</span></article></Reveal>
              </div>
            </div>
          </div>
        </section>

        <section className="resume-section" id="resume">
          <div className="resume-orb" aria-hidden="true" />
          <div className="container resume-inner"><Reveal className="resume-copy"><p className="eyebrow"><span>06</span> READY FOR WHAT’S NEXT</p><h2>Let’s make<br /><span>something happen.</span></h2><p>Explore my resume to learn more about my technical skills, training, and development projects.</p><div className="resume-actions">{resumeReady ? <a className="button button--light" href={profile.resumePath} download data-cursor="DOWNLOAD">Download resume <ArrowDownRight size={16} /></a> : <button className="button button--light button--resume-disabled" type="button" disabled>Resume PDF coming soon <ArrowDownRight size={16} /></button>}<span>PDF resume · latest details in the attached CV</span></div></Reveal><Reveal className="resume-stamp" delay={0.14}><div className="stamp-ring"><span className="stamp-top">SWETHA BIJU · PORTFOLIO</span><span className="stamp-monogram">SB<span>.</span></span><span className="stamp-bottom">AVAILABLE FOR OPPORTUNITIES</span></div><div className="stamp-star">✳</div></Reveal></div>
        </section>

        <section className="contact-section section-pad" id="contact">
          <div className="container">
            <Reveal><SectionHeading index="07" eyebrow="SAY HELLO, START SOMETHING" title={<>Got something<br className="mobile-break" /> interesting in mind<span className="mint-period">?</span></>} note="New opportunities welcome." /></Reveal>
            <div className="contact-layout">
              <Reveal className="contact-copy">
                <p className="contact-lead">I’m looking for an opportunity to grow, contribute, and build useful things with a great team. Let’s connect.</p>
                <div className="contact-links">
                  <a href={profile.githubUrl} target="_blank" rel="noreferrer" data-cursor="OPEN"><span className="contact-link-icon"><GitHubMark size={17} /></span><span><small>GITHUB</small><b>github.com/swetha-963</b></span><ExternalLink size={14} /></a>
                  <a href={`mailto:${profile.email}`}><span className="contact-link-icon"><Mail size={17} /></span><span><small>EMAIL</small><b>{profile.email}</b></span><ArrowRight size={14} /></a>
                  <a href={profile.linkedinUrl} target="_blank" rel="noreferrer" data-cursor="OPEN"><span className="contact-link-icon"><span className="linkedin-mark">in</span></span><span><small>LINKEDIN</small><b>linkedin.com/in/swetha-biju-321a8434a</b></span><ExternalLink size={14} /></a>
                </div>
                <div className="contact-availability"><span className="availability-dot" /><span>OPEN TO ENTRY-LEVEL IT OPPORTUNITIES</span></div>
              </Reveal>
              <Reveal className="contact-form-wrap" delay={0.1}><div className="form-heading"><span>01 <span>/</span> SEND A NOTE</span><ArrowDownRight size={17} /></div><ContactForm /></Reveal>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-main"><a className="wordmark footer-wordmark" href="#home" aria-label="Back to top"><span className="wordmark-symbol">S<span>.</span></span><span className="wordmark-name">SWETHA BIJU</span></a><p>Designed & built by Swetha Biju<span>.</span></p><div className="footer-links"><a href={profile.githubUrl} target="_blank" rel="noreferrer" aria-label="GitHub" data-cursor="OPEN"><GitHubMark size={16} /></a>{linkedinReady ? <a href={profile.linkedinUrl} target="_blank" rel="noreferrer" aria-label="LinkedIn" data-cursor="OPEN"><span className="linkedin-mark">in</span></a> : <span className="footer-link-pending" aria-label="LinkedIn URL pending"><span className="linkedin-mark">in</span></span>}<button type="button" onClick={() => window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' })} aria-label="Back to top" data-cursor="UP"><ArrowUp size={16} /></button></div></div>
        <div className="container footer-bottom"><span>© {year} SWETHA BIJU</span><span>MADE WITH CURIOSITY <span className="footer-heart">✳</span> IN KERALA, INDIA</span><a href="#home">BACK TO TOP ↑</a></div>
      </footer>
      <button className={`back-to-top ${scrolled ? 'is-visible' : ''}`} type="button" onClick={() => window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' })} aria-label="Back to top" data-cursor="UP"><ArrowUp size={17} /></button>
    </div>
  );
}

export default App;
