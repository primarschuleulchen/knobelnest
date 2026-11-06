# 12) iPad hochkant (700–1000 px breit): Listen links und rechts neben dem Weg wie im Querformat, ohne Scrollen
rep('@media (min-width:901px){', '@media (min-width:700px){')
rep('@media (max-width:900px){', '@media (max-width:699px){')
rep('if(innerWidth<=900){', 'if(innerWidth<700){')
rep('''@media (max-width:480px){.facts{''', '''@media (min-width:700px) and (max-width:1000px){
  .stage{grid-template-columns:minmax(0,1fr) minmax(0,1.15fr) minmax(0,1fr);gap:10px}
  .facts:not([style]){grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
  .facts:not([style])>:nth-child(n+3){display:none}
  .kid{grid-template-columns:calc(var(--r) * 1.05) minmax(0,1fr);gap:0 6px;padding:calc(var(--r) * .05) 4px}
  .kname{font-size:clamp(14px,calc(var(--r) * .3),22px)}
  .kname .st{display:none}
  .lhead{font-size:20px;padding:6px 10px 2px}
}
@media (max-width:480px){.facts{''')
