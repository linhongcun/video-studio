# EP.22 pronunciation.md（v0.29.0，change-list-v9 无比喻版）

送 TTS 的文本里多音字有风险时换同音字或改周围的词；稿子和字幕保持原字。按 research.md v0.3.4 多音字表执行，并按 11 段 script.md 逐词扫过旁白（Miyazaki 2026-10-16）。Redis、MySQL 按一个单词读；TTL、EoL 逐字母。读音由 Knoll 和 Nolan 自核。配音：冰糖。

## 全文多音字与专名

| 词 | 读音 | 位置 / 说明 |
|---|---|---|
| 重试 | **chóng shì** | retry / eventual / recap；不能读 zhòng |
| 更新 | **gēng xīn** | 画面术语「更新缓存」；旁白未念，若补念不能读 gèng |
| 收藏 | **shōu cáng** | ending；不能读 zàng |
| 设得 | **shè de（助词）** | ttl；不能读 děi |
| 一致 | **yí zhì** | eventual；去声前读 yí |
| 一次 | **yí cì** | del；去声前读 yí |
| 一份 | **yí fèn** | copies；去声前读 yí |
| 一会儿 | **yí huìr** | eventual；去声前读 yí |
| 一套 | **yí tào** | retry；去声前读 yí |
| 一道 | **yí dào** | ttl；去声前读 yí |
| 一个 | **yí gè** | hook「一个一个」；去声前读 yí |
| 一时 | **yì shí** | retry；非去声前读 yì |
| 一直 | **yì zhí** | retry；非去声前读 yì |
| 一交错 | **yì jiāo cuò** | del；非去声前读 yì |
| 还是 | **hái shì** | hook / ending；不能读 huán |
| 还有 | **hái yǒu** | ttl；不能读 huán |
| 还没 | **hái méi** | order / replica；不能读 huán |
| 数据 | **shù jù** | 多章；不能读 shǔ |
| 从库 | **cóng kù** | replica；不能读 zòng |
| 主从 | **zhǔ cóng** | replica / recap；不能读 zòng |
| 空隙 | **kòng xì** | read / order；不能读 kōng |
| 处理 | **chǔ lǐ** | （文章）；不能读 chù |
| 转人工 | **zhuǎn rén gōng** | retry；不能读 zhuàn |
| 降低 | **jiàng dī** | order；不能读 xiáng |
| 压力 | **yā lì** | replica；— |
| 了 | **le（改了、失败了）** | hook / retry / ending；不能读 liǎo |
| MySQL | **按一个单词读** | copies / retry；不逐字母 |
| Redis | **按一个单词读（近「瑞迪斯」）** | copies / retry；不逐字母 |
| Cache-Aside | **英文两个词「cache aside」** | read；不逐字母；画面只写「旁路缓存」 |
| binlog | **英文一个词「bin log」** | retry；不逐字母；画面只写「变更日志」 |
| TTL | **逐字母 T-T-L** | ttl；— |
| EoL | **逐字母 E-O-L** | copies；旁白「进入 EoL」；不读成单词 |
| App | **按一个单词读** | ending；片尾问题句 |
| 加重 | **jiā zhòng** | （若出现）；不能读 chóng |
| 觉得 | **jué de** | ending；不能读 jiào |
| 算数 | **suàn shù** | copies；不能读 shǔ |
| 得靠 | **děi kào（必须）** | eventual「再靠」读 kào；— |
| 八点四点十一 | **bā diǎn sì diǎn shí yī** | copies；对应 MySQL 8.4.11 |
| 八点零 | **bā diǎn líng** | copies；对应 MySQL 8.0 |
| 八点零点四十六 | **bā diǎn líng diǎn sì shí liù** | copies；对应 8.0.46 |
| 时间差 | **shí jiān chā** | （文章）；不能读 chà / chāi |
| 一般 | **yì bān** | del / retry / replica；非去声前读 yì |
| 适合 | **shì hé** | del / replica；— |
| 就要 | **jiù yào** | replica；要读 yào |
| 库存 | **kù cún** | replica；— |
| 结账 | **jié zhàng** | eventual；不能读 jiē |
| 设多长 | **shè duō cháng** | ttl；不能读 zhǎng |
| 换个坑 | **huàn gè kēng** | order / replica 开场；— |
| 挡不住 | **dǎng bú zhù** | replica；— |

## 「只」通则

旁白里的「只」全部是副词 **zhǐ**（只看、只按），不能读 zhī。

## 「一」通则

单念、序数、末尾读原调 **yī**；去声前读 **yí**（一次、一份、一会儿、一套、一道、一个、一致）；非去声前读 **yì**（一种、一时、一直、一交错、一般）。本期不说「第一层」等序数层名。
