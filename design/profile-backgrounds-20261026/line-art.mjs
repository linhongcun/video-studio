const wrap = (content) => `<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="1500" viewBox="0 0 1500 1500" fill="none">${content}</svg>`;

const roof = (x, y, size, opacity = 1) => `<g transform="translate(${x} ${y}) scale(${size / 180})" opacity="${opacity}"><path d="M0 72 90 0 180 72" stroke="#82e9db" stroke-width="4.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M24 73v111h132V73" fill="#112c32" stroke="#82e9db" stroke-width="2.5" stroke-linejoin="round"/><path d="M71 184v-52h38v52" stroke="#82e9db" stroke-width="2.2"/><path d="M48 102h22v22H48zm63 0h22v22h-22z" fill="#dab987" fill-opacity=".8"/></g>`;

const stars = (prefix, color, count = 32) => Array.from({length: count}, (_, i) => {
  const x = 40 + ((i * 197 + 31) % 1420);
  const y = 90 + ((i * 113 + 67) % 710);
  const r = i % 7 === 0 ? 1.9 : 1;
  return `<circle cx="${x}" cy="${y}" r="${r}" fill="${color}" opacity="${i % 7 === 0 ? '.28' : '.13'}"/>`;
}).join('');

const blueGrid = Array.from({length: 20}, (_, i) => `<path d="M${i * 100} 0v1050M0 ${i * 100}h1500" stroke="#5b9394" stroke-width="1"/>`).join('');

const contours = Array.from({length: 17}, (_, i) => {
  const a = i * 18;
  return `<path d="M${1510 + a * .22} ${1050 - a * .18}C${1200 - a * .12} ${925 - a * .1} ${1425 - a * .8} ${730 - a * .58} ${1224 - a * .17} ${600 - a * .45}S${940 - a * .05} ${372 - a * .22} ${1120 + a * .42} ${196 + a * .1}" stroke="#77d2bb" stroke-width="${i % 5 === 0 ? 2.2 : 1.1}" opacity="${i % 5 === 0 ? '.39' : '.2'}"/>`;
}).join('');

export default [
  {
    id: '01', slug: 'midnight-code-village', name: '深夜小村',
    description: '深蓝夜色里的屋檐与微光，把代码小村延伸成一片安静的背景。',
    background: '#0d1b29', accent: '#82e9db',
    svg: wrap(`
      <defs>
        <linearGradient id="bg01-base" x1="180" y1="0" x2="1180" y2="1500" gradientUnits="userSpaceOnUse"><stop stop-color="#142c3b"/><stop offset=".55" stop-color="#0c1e2d"/><stop offset="1" stop-color="#0b1522"/></linearGradient>
        <radialGradient id="bg01-light" cx="0" cy="0" r="1" gradientTransform="translate(1210 470) rotate(90) scale(480 510)" gradientUnits="userSpaceOnUse"><stop stop-color="#376a66" stop-opacity=".38"/><stop offset="1" stop-color="#376a66" stop-opacity="0"/></radialGradient>
        <linearGradient id="bg01-floor" x1="0" y1="630" x2="0" y2="1120" gradientUnits="userSpaceOnUse"><stop stop-color="#0d1b29" stop-opacity="0"/><stop offset="1" stop-color="#0d1826"/></linearGradient>
      </defs>
      <rect width="1500" height="1500" fill="url(#bg01-base)"/>
      <rect width="1500" height="1200" fill="url(#bg01-light)"/>
      ${stars('bg01', '#a6d6c8')}
      <path d="M-140 834C155 711 400 784 610 708S1045 620 1640 724" stroke="#598e87" stroke-opacity=".1" stroke-width="2"/>
      <path d="M-120 872C210 758 382 825 646 753S1111 673 1620 767" stroke="#598e87" stroke-opacity=".065" stroke-width="2"/>
      <path d="M995 615h107v-51h133v74h136v-52h129" stroke="#82e9db" stroke-opacity=".23" stroke-width="2"/>
      ${roof(1010, 426, 127, .3)}
      ${roof(1136, 304, 184, .75)}
      ${roof(1322, 438, 124, .36)}
      <path d="M1227 511v74h-106v51H992" stroke="#7cd8c6" stroke-opacity=".35" stroke-width="2.2"/>
      <circle cx="1227" cy="585" r="5" fill="#8ce3cd" fill-opacity=".65"/>
      <circle cx="1121" cy="636" r="4" fill="#e2c597" fill-opacity=".55"/>
      <rect y="620" width="1500" height="880" fill="url(#bg01-floor)"/>
      <path d="M0 1140C440 1035 860 1105 1500 920v580H0Z" fill="#0c1724" fill-opacity=".65"/>
    `)
  },
  {
    id: '02', slug: 'knowledge-constellation', name: '知识星图',
    description: '稀疏轨道与相连的光点，表达技术知识之间逐渐建立的联系。',
    background: '#111c32', accent: '#a2c4f5',
    svg: wrap(`
      <defs>
        <linearGradient id="bg02-base" x1="100" y1="0" x2="1400" y2="1400" gradientUnits="userSpaceOnUse"><stop stop-color="#14263b"/><stop offset=".48" stop-color="#111d32"/><stop offset="1" stop-color="#0c1524"/></linearGradient>
        <radialGradient id="bg02-glow" cx="0" cy="0" r="1" gradientTransform="translate(1225 425) rotate(90) scale(550 540)" gradientUnits="userSpaceOnUse"><stop stop-color="#41609d" stop-opacity=".25"/><stop offset="1" stop-color="#41609d" stop-opacity="0"/></radialGradient>
        <linearGradient id="bg02-fade" x1="0" y1="590" x2="0" y2="1090" gradientUnits="userSpaceOnUse"><stop stop-color="#0d1728" stop-opacity="0"/><stop offset="1" stop-color="#0d1728"/></linearGradient>
      </defs>
      <rect width="1500" height="1500" fill="url(#bg02-base)"/>
      <rect width="1500" height="1100" fill="url(#bg02-glow)"/>
      ${stars('bg02', '#bcd4ee', 48)}
      <g stroke="#8cadde" stroke-width="1.5">
        <ellipse cx="1230" cy="424" rx="319" ry="220" transform="rotate(-24 1230 424)" stroke-opacity=".28"/>
        <ellipse cx="1230" cy="424" rx="390" ry="130" transform="rotate(42 1230 424)" stroke-opacity=".16"/>
        <ellipse cx="1230" cy="424" rx="205" ry="327" transform="rotate(32 1230 424)" stroke-opacity=".16"/>
        <circle cx="1230" cy="424" r="104" stroke-opacity=".1"/>
        <path d="m1011 330 134-72 198 57 43 180-178 113-197-112 134-238 241 237" stroke-opacity=".15"/>
      </g>
      <g fill="#a5e8d7"><circle cx="1011" cy="330" r="6" fill-opacity=".7"/><circle cx="1343" cy="315" r="7" fill-opacity=".8"/><circle cx="1208" cy="608" r="5" fill-opacity=".45"/><circle cx="1386" cy="495" r="5" fill-opacity=".65"/></g>
      <circle cx="1145" cy="258" r="8" fill="#efc892" fill-opacity=".85"/>
      <circle cx="1145" cy="258" r="18" stroke="#efc892" stroke-opacity=".14" stroke-width="6"/>
      <circle cx="1230" cy="424" r="13" fill="#b5d3ed" fill-opacity=".7"/>
      <circle cx="1230" cy="424" r="31" stroke="#aac8f4" stroke-opacity=".12" stroke-width="12"/>
      <rect y="590" width="1500" height="910" fill="url(#bg02-fade)"/>
    `)
  },
  {
    id: '03', slug: 'engineering-blueprint', name: '工程蓝图',
    description: '格网与等距结构只留在画面边缘，保持工程感，也让主页资料清楚。',
    background: '#0c252c', accent: '#79c5bb',
    svg: wrap(`
      <defs>
        <linearGradient id="bg03-base" x1="0" y1="0" x2="1400" y2="1500" gradientUnits="userSpaceOnUse"><stop stop-color="#103039"/><stop offset=".55" stop-color="#102730"/><stop offset="1" stop-color="#0b1b28"/></linearGradient>
        <radialGradient id="bg03-glow" cx="0" cy="0" r="1" gradientTransform="translate(1250 430) rotate(90) scale(470 540)" gradientUnits="userSpaceOnUse"><stop stop-color="#3e8277" stop-opacity=".2"/><stop offset="1" stop-color="#3e8277" stop-opacity="0"/></radialGradient>
        <linearGradient id="bg03-fade" x1="0" y1="520" x2="0" y2="1000" gradientUnits="userSpaceOnUse"><stop stop-color="#0c202c" stop-opacity="0"/><stop offset="1" stop-color="#0c202c"/></linearGradient>
      </defs>
      <rect width="1500" height="1500" fill="url(#bg03-base)"/>
      <g opacity=".075">${blueGrid}</g>
      <rect width="1500" height="1050" fill="url(#bg03-glow)"/>
      <g stroke="#88d9c9" stroke-width="2" stroke-linejoin="round">
        <path d="m1065 344 170-98 170 98-170 98Z" fill="#1b464b" stroke-opacity=".5"/>
        <path d="m1065 344 170 98v196l-170-98Z" fill="#123239" stroke-opacity=".36"/>
        <path d="m1235 442 170-98v196l-170 98Z" fill="#14383e" stroke-opacity=".5"/>
        <path d="m1150 294 170 98m-170 1 170-99m-255 148 170 98 170-98m-170 98v98" stroke-opacity=".17"/>
        <path d="m925 621 140-80 170 98 170-98 155 89-325 187Z" stroke-opacity=".13"/>
        <path d="m994 581 170 98 171-98m-341 80 171 98m-30-178-170 98m170 40 170-98" stroke-opacity=".08"/>
      </g>
      <path d="M1430 326h37v248h-37M1040 344h-37v196h37" stroke="#88d9c9" stroke-opacity=".24" stroke-width="1.5"/>
      <circle cx="1235" cy="246" r="5" fill="#e8c693" fill-opacity=".8"/>
      <circle cx="1405" cy="540" r="4" fill="#91e6ce" fill-opacity=".75"/>
      <path d="M60 250h55m-55 0v55M1440 1080h-55m55 0v-55" stroke="#86c6bc" stroke-opacity=".11" stroke-width="2"/>
      <rect y="520" width="1500" height="980" fill="url(#bg03-fade)"/>
    `)
  },
  {
    id: '04', slug: 'algorithm-garden', name: '算法花园',
    description: '薄荷色曲线像叶脉一样展开，在留白里呈现有秩序的生长。',
    background: '#10292b', accent: '#77d2bb',
    svg: wrap(`
      <defs>
        <linearGradient id="bg04-base" x1="300" y1="0" x2="1200" y2="1500" gradientUnits="userSpaceOnUse"><stop stop-color="#123338"/><stop offset=".55" stop-color="#10262d"/><stop offset="1" stop-color="#0b1825"/></linearGradient>
        <radialGradient id="bg04-glow" cx="0" cy="0" r="1" gradientTransform="translate(1260 450) rotate(90) scale(520 440)" gradientUnits="userSpaceOnUse"><stop stop-color="#467865" stop-opacity=".3"/><stop offset="1" stop-color="#467865" stop-opacity="0"/></radialGradient>
        <linearGradient id="bg04-fade" x1="0" y1="650" x2="0" y2="1120" gradientUnits="userSpaceOnUse"><stop stop-color="#0d1e2b" stop-opacity="0"/><stop offset="1" stop-color="#0d1e2b"/></linearGradient>
      </defs>
      <rect width="1500" height="1500" fill="url(#bg04-base)"/>
      <rect width="1500" height="1150" fill="url(#bg04-glow)"/>
      ${contours}
      <path d="M1472 824C1277 733 1434 558 1267 431S1115 283 1258 219" stroke="#b5dfbd" stroke-opacity=".42" stroke-width="2.8"/>
      <path d="M1267 431c92 9 139-18 170-93m-142 163c-74 9-126-12-163-60m242 184c-14-72 18-122 96-152" stroke="#9cd3b6" stroke-opacity=".3" stroke-width="1.8"/>
      <circle cx="1258" cy="219" r="5" fill="#e2c592" fill-opacity=".65"/>
      <circle cx="1437" cy="338" r="4" fill="#9bdfc3" fill-opacity=".6"/>
      <circle cx="1132" cy="441" r="4" fill="#9bdfc3" fill-opacity=".45"/>
      <rect y="650" width="1500" height="850" fill="url(#bg04-fade)"/>
      <path d="M-60 1180C410 1040 790 1260 1560 1030" stroke="#77b9a7" stroke-opacity=".025" stroke-width="3"/>
    `)
  }
];
