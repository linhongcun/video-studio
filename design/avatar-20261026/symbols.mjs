const wrap = (name, content) => `<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024" role="img" aria-label="${name}">${content}</svg>`;

export default [
  {
    id: '01', slug: 'code-village', name: '代码小村', family: '符号',
    description: '把代码括号放进小村屋檐，直接联系名称与技术内容。',
    background: '#101d2d', accent: '#82e9db',
    svg: wrap('代码小村', `
      <rect width="1024" height="1024" fill="#101d2d"/>
      <circle cx="512" cy="512" r="386" fill="none" stroke="#263c4b" stroke-width="3"/>
      <path d="M269 453 512 250 755 453" fill="none" stroke="#82e9db" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M330 454v256q0 32 32 32h300q32 0 32-32V454" fill="none" stroke="#82e9db" stroke-width="36" stroke-linecap="round"/>
      <path d="m450 506-67 64 67 64m124-128 67 64-67 64" fill="none" stroke="#eef8f4" stroke-width="33" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="m533 494-43 151" stroke="#82e9db" stroke-width="28" stroke-linecap="round"/>
      <circle cx="755" cy="302" r="21" fill="#f4c889"/>
      <path d="M234 785h85m386 0h85" stroke="#39505c" stroke-width="7" stroke-linecap="round"/>
    `)
  },
  {
    id: '02', slug: 'open-source-book', name: '翻开原理', family: '符号',
    description: '沿用站点书本意象，加入代码，强调短片与图文一起讲清原理。',
    background: '#17332f', accent: '#c8f2d5',
    svg: wrap('翻开原理', `
      <rect width="1024" height="1024" fill="#17332f"/>
      <circle cx="512" cy="498" r="350" fill="#1e4039"/>
      <path d="M256 309q141-34 256 51 115-85 256-51v345q-141-29-256 57-115-86-256-57Z" fill="#c8f2d5"/>
      <path d="M512 360v351" stroke="#17332f" stroke-width="18"/>
      <path d="M284 693q120-13 228 60 108-73 228-60" fill="none" stroke="#f3c78a" stroke-width="18" stroke-linecap="round"/>
      <path d="m371 432-49 51 49 51m49-87v107" fill="none" stroke="#24574a" stroke-width="23" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="m653 432 49 51-49 51m-49-87v107" fill="none" stroke="#24574a" stroke-width="23" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="m350 588 83 15m158 0 83-15" stroke="#6b9b7a" stroke-width="16" stroke-linecap="round"/>
      <path d="m490 236 22-36 22 36" fill="none" stroke="#f3c78a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
    `)
  },
  {
    id: '03', slug: 'code-in-motion', name: '代码开演', family: '符号',
    description: '代码括号与播放键合为一个符号，呼应“用代码拍科普”。',
    background: '#f1e6cf', accent: '#246258',
    svg: wrap('代码开演', `
      <rect width="1024" height="1024" fill="#f1e6cf"/>
      <circle cx="512" cy="512" r="366" fill="#e8dcc2"/>
      <path d="m361 319-148 193 148 193m302-386 148 193-148 193" fill="none" stroke="#17352f" stroke-width="54" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M432 378q0-25 22-12l181 127q24 16 0 33L454 653q-22 14-22-12Z" fill="#246258"/>
      <path d="M448 401v209l149-105Z" fill="#448575" opacity=".55"/>
      <circle cx="512" cy="787" r="16" fill="#b87a42"/>
    `)
  },
  {
    id: '04', slug: 'logic-tree', name: '逻辑生长', family: '符号',
    description: '三个节点与清楚的分支，提取算法、系统连接与逐步推导的共同特征。',
    background: '#202439', accent: '#beb5f4',
    svg: wrap('逻辑生长', `
      <rect width="1024" height="1024" fill="#202439"/>
      <circle cx="512" cy="512" r="367" fill="none" stroke="#3c405b" stroke-width="3"/>
      <path d="M512 367v94q0 47-47 47h-99q-47 0-47 47v60m193-154q0 47 47 47h99q47 0 47 47v60" fill="none" stroke="#beb5f4" stroke-width="30" stroke-linecap="round"/>
      <rect x="433" y="227" width="158" height="158" rx="49" fill="#beb5f4"/>
      <rect x="235" y="601" width="168" height="168" rx="53" fill="#8edccc"/>
      <rect x="621" y="601" width="168" height="168" rx="53" fill="#f2c88d"/>
      <circle cx="512" cy="306" r="23" fill="#202439"/>
      <path d="m293 685 19 19 34-39" fill="none" stroke="#20493e" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M680 685h50m-25-25v50" stroke="#78572e" stroke-width="16" stroke-linecap="round"/>
    `)
  }
];
