const svg = (background, content, definitions = '') => `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" fill="none"><defs>${definitions}</defs><rect width="1024" height="1024" fill="${background}"/>${content}</svg>`;

export default [
  {
    id: '05',
    slug: 'village-coder',
    name: '技术村民',
    family: '角色',
    description: '圆框眼镜和薄荷色衣领，亲和的技术讲解者。',
    background: '#102A30',
    accent: '#82E9DB',
    svg: svg('#102A30', `
      <circle cx="512" cy="492" r="342" fill="#143B40"/>
      <circle cx="512" cy="492" r="342" stroke="#4E9F96" stroke-opacity=".28" stroke-width="3"/>
      <path d="M238 820c15-137 111-217 274-217s259 80 274 217H238Z" fill="#82E9DB"/>
      <path d="m442 641 70 66 70-66v-86H442v86Z" fill="#E6AC89"/>
      <path d="m387 662 125 115 125-115-46-29-79 74-79-74-46 29Z" fill="#42B8AA"/>
      <path d="m477 744 35 33 35-33v76h-70v-76Z" fill="#D3FFF2"/>
      <path d="M337 383c-37-12-62 14-57 55 4 34 23 56 54 57m353-112c37-12 62 14 57 55-4 34-23 56-54 57" fill="#F1BD9D"/>
      <path d="M324 364c0-126 73-180 188-180s188 54 188 180v115c0 111-84 183-188 183s-188-72-188-183V364Z" fill="#FFD0AE"/>
      <path d="M324 405v-72c0-109 79-161 185-161 55 0 102 14 133 41 43 8 70 48 66 102l-8 90-48-77c-56 15-149 10-195-41-12 47-56 79-94 89l-39 29Z" fill="#092026"/>
      <path d="M384 341c45-16 69-47 75-79 49 48 121 61 185 52" stroke="#205156" stroke-width="14" stroke-linecap="round"/>
      <g stroke="#17333A" stroke-width="17">
        <circle cx="421" cy="437" r="67"/>
        <circle cx="603" cy="437" r="67"/>
        <path d="M488 431c14-13 34-13 48 0M354 421l-31-13m347 13 31-13" stroke-linecap="round"/>
      </g>
      <path d="M410 436v17m182-17v17" stroke="#17333A" stroke-width="17" stroke-linecap="round"/>
      <path d="m506 463-9 44h24" stroke="#D9916C" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M463 546c28 25 70 25 98 0" stroke="#17333A" stroke-width="13" stroke-linecap="round"/>
      <path d="m381 749-27 21 27 21m262-42 27 21-27 21" stroke="#17333A" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
    `),
  },
  {
    id: '06',
    slug: 'bracket-friend',
    name: '括号小友',
    family: '角色',
    description: '把代码花括号变成一张笑脸，简洁又容易记住。',
    background: '#82E9DB',
    accent: '#102A30',
    svg: svg('#82E9DB', `
      <circle cx="512" cy="512" r="340" fill="#A1F5E7"/>
      <path d="M357 273h-28c-33 0-53 21-53 53v91c0 43-19 69-53 84 34 15 53 41 53 84v91c0 32 20 53 53 53h28" stroke="#102A30" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M667 273h28c33 0 53 21 53 53v91c0 43 19 69 53 84-34 15-53 41-53 84v91c0 32-20 53-53 53h-28" stroke="#102A30" stroke-width="50" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="m454 263 58 41 58-41-58-41-58 41Z" fill="#F17D5B"/>
      <path d="M428 440v56m168-56v56" stroke="#102A30" stroke-width="39" stroke-linecap="round"/>
      <path d="M437 570c38 47 112 47 150 0" stroke="#102A30" stroke-width="27" stroke-linecap="round"/>
      <circle cx="373" cy="534" r="18" fill="#39B9A5"/>
      <circle cx="651" cy="534" r="18" fill="#39B9A5"/>
      <path d="M474 749h76" stroke="#39B9A5" stroke-width="17" stroke-linecap="round"/>
    `),
  },
  {
    id: '07',
    slug: 'pixel-villager',
    name: '像素村民',
    family: '角色',
    description: '用少量像素塑造程序员形象，带一点早期计算机的趣味。',
    background: '#181E3C',
    accent: '#C4B7FF',
    svg: svg('#181E3C', `
      <path d="M288 192h448v64h64v448h-64v64H288v-64h-64V256h64v-64Z" fill="#252E53"/>
      <g shape-rendering="crispEdges">
        <path d="M352 224h256v32h64v64h32v224h-32v64h-64v32H416v-32h-64v-64h-32V320h32v-96Z" fill="#F5C9A9"/>
        <path d="M352 224h256v32h64v64h32v64h-64v-64H480v64H352v64h-32V320h32v-96Z" fill="#C4B7FF"/>
        <path d="M352 224h256v32H416v32h-64v-64Z" fill="#E1D9FF"/>
        <path d="M416 416h64v64h-64v-64Zm160 0h64v64h-64v-64Z" fill="#181E3C"/>
        <path d="M416 416h32v32h-32v-32Zm160 0h32v32h-32v-32Z" fill="#FFF3E9"/>
        <path d="M448 544h128v32H448v-32Z" fill="#181E3C"/>
        <path d="M448 640h128v32h64v32h64v64h32v64H288v-64h32v-64h64v-32h64v-32Z" fill="#82E9DB"/>
        <path d="M448 640h128v32h-32v32h-64v-32h-32v-32Z" fill="#E2AB8A"/>
        <path d="M384 704h32v128h-32V704Zm224 0h32v128h-32V704Z" fill="#3CB1A8"/>
        <path d="M480 752h64v32h-64v-32Z" fill="#181E3C"/>
        <path d="M224 448h32v32h-32v-32Zm544-128h32v32h-32v-32Z" fill="#C4B7FF"/>
      </g>
    `),
  },
  {
    id: '08',
    slug: 'curious-owl',
    name: '好奇小鸮',
    family: '角色',
    description: '睁眼观察、翻书理解，用学习伙伴表达技术科普的耐心。',
    background: '#2A2446',
    accent: '#E6D8FF',
    svg: svg('#2A2446', `
      <circle cx="512" cy="506" r="336" fill="#3A315B"/>
      <path d="m294 377-4-141 153 80m287 61 4-141-153 80" fill="#BCA7EC"/>
      <path d="M276 465c0-137 104-224 236-224s236 87 236 224v109c0 125-101 221-236 221s-236-96-236-221V465Z" fill="#BCA7EC"/>
      <path d="M306 434c0-80 42-131 103-131 43 0 76 20 103 58 27-38 60-58 103-58 61 0 103 51 103 131 0 106-86 194-206 194S306 540 306 434Z" fill="#E8DFFF"/>
      <circle cx="412" cy="444" r="70" fill="#2A2446"/>
      <circle cx="612" cy="444" r="70" fill="#2A2446"/>
      <circle cx="428" cy="424" r="22" fill="#F7F1FF"/>
      <circle cx="628" cy="424" r="22" fill="#F7F1FF"/>
      <path d="m478 520 34 42 34-42-34-21-34 21Z" fill="#F5BA74"/>
      <path d="M512 663c-78-51-157-66-252-54v150c97-10 176 4 252 54 76-50 155-64 252-54V609c-95-12-174 3-252 54Z" fill="#F5EEDC"/>
      <path d="M512 663v150c76-50 155-64 252-54V609c-95-12-174 3-252 54Z" fill="#D6C6F2"/>
      <path d="M512 671v142" stroke="#2A2446" stroke-width="12" stroke-linecap="round"/>
      <path d="M314 662c50 0 92 10 137 33m-137 19c50 0 92 10 137 33m259-85c-50 0-92 10-137 33m137 19c-50 0-92 10-137 33" stroke="#9985B7" stroke-width="12" stroke-linecap="round"/>
      <path d="M279 571c-38 22-53 66-27 104 13 18 42 12 55-6l36-49-64-49Zm466 0c38 22 53 66 27 104-13 18-42 12-55-6l-36-49 64-49Z" fill="#BCA7EC"/>
    `),
  },
];
