/**
 * 亮星名称映射表
 * HIP编号 -> 星星名称（中文 + 英文）
 */

export interface StarName {
    hip: number;
    chinese: string;
    english: string;
    constellation: string;  // 所属星座
    bayer?: string;        // 拜耳命名（如 α Ori）
}

export const BRIGHT_STAR_NAMES: StarName[] = [
    // 天狼星 - 最亮的恒星
    { hip: 32349, chinese: '天狼星', english: 'Sirius', constellation: '大犬座', bayer: 'α CMa' },
    
    // 老人星 - 第二亮
    { hip: 30438, chinese: '老人星', english: 'Canopus', constellation: '船底座', bayer: 'α Car' },
    
    // 南门二 - 第三亮，半人马座α
    { hip: 71683, chinese: '南门二', english: 'Rigil Kentaurus', constellation: '半人马座', bayer: 'α Cen' },
    
    // 大角星 - 牧夫座α
    { hip: 69673, chinese: '大角星', english: 'Arcturus', constellation: '牧夫座', bayer: 'α Boo' },
    
    // 织女星 - 天琴座α
    { hip: 91262, chinese: '织女星', english: 'Vega', constellation: '天琴座', bayer: 'α Lyr' },
    
    // 五车二 - 御夫座α
    { hip: 24608, chinese: '五车二', english: 'Capella', constellation: '御夫座', bayer: 'α Aur' },
    
    // 参宿七 - 猎户座β
    { hip: 24436, chinese: '参宿七', english: 'Rigel', constellation: '猎户座', bayer: 'β Ori' },
    
    // 南河三 - 小犬座α
    { hip: 37279, chinese: '南河三', english: 'Procyon', constellation: '小犬座', bayer: 'α CMi' },
    
    // 参宿四 - 猎户座α
    { hip: 27989, chinese: '参宿四', english: 'Betelgeuse', constellation: '猎户座', bayer: 'α Ori' },
    
    // 水委一 - 波江座α
    { hip: 7588, chinese: '水委一', english: 'Achernar', constellation: '波江座', bayer: 'α Eri' },
    
    // 马腹一 - 半人马座β
    { hip: 68702, chinese: '马腹一', english: 'Hadar', constellation: '半人马座', bayer: 'β Cen' },
    
    // 牛郎星/河鼓二 - 天鹰座α
    { hip: 97649, chinese: '牛郎星', english: 'Altair', constellation: '天鹰座', bayer: 'α Aql' },
    
    // 十字架二 - 南十字座α
    { hip: 60718, chinese: '十字架二', english: 'Acrux', constellation: '南十字座', bayer: 'α Cru' },
    
    // 毕宿五 - 金牛座α
    { hip: 21421, chinese: '毕宿五', english: 'Aldebaran', constellation: '金牛座', bayer: 'α Tau' },
    
    // 心宿二 - 天蝎座α
    { hip: 80763, chinese: '心宿二', english: 'Antares', constellation: '天蝎座', bayer: 'α Sco' },
    
    // 角宿一 - 室女座α
    { hip: 65474, chinese: '角宿一', english: 'Spica', constellation: '室女座', bayer: 'α Vir' },
    
    // 北落师门 - 南鱼座α
    { hip: 113368, chinese: '北落师门', english: 'Fomalhaut', constellation: '南鱼座', bayer: 'α PsA' },
    
    // 天津四 - 天鹅座α
    { hip: 102098, chinese: '天津四', english: 'Deneb', constellation: '天鹅座', bayer: 'α Cyg' },
    
    // 轩辕十四 - 狮子座α
    { hip: 49669, chinese: '轩辕十四', english: 'Regulus', constellation: '狮子座', bayer: 'α Leo' },
    
    // 十字架三 - 南十字座β
    { hip: 62434, chinese: '十字架三', english: 'Mimosa', constellation: '南十字座', bayer: 'β Cru' },
    
    // 参宿五 - 猎户座ε
    { hip: 26311, chinese: '参宿五', english: 'Alnilam', constellation: '猎户座', bayer: 'ε Ori' },
    
    // 参宿一 - 猎户座ζ
    { hip: 26727, chinese: '参宿一', english: 'Alnitak', constellation: '猎户座', bayer: 'ζ Ori' },
    
    // 参宿二 - 猎户座δ
    { hip: 25336, chinese: '参宿二', english: 'Mintaka', constellation: '猎户座', bayer: 'δ Ori' },
    
    // 北极星 - 小熊座α
    { hip: 11767, chinese: '北极星', english: 'Polaris', constellation: '小熊座', bayer: 'α UMi' },
    
    // 北斗七星
    { hip: 54061, chinese: '天枢', english: 'Dubhe', constellation: '大熊座', bayer: 'α UMa' },
    { hip: 53910, chinese: '天璇', english: 'Merak', constellation: '大熊座', bayer: 'β UMa' },
    { hip: 58001, chinese: '天玑', english: 'Phecda', constellation: '大熊座', bayer: 'γ UMa' },
    { hip: 59774, chinese: '天权', english: 'Megrez', constellation: '大熊座', bayer: 'δ UMa' },
    { hip: 62956, chinese: '玉衡', english: 'Alioth', constellation: '大熊座', bayer: 'ε UMa' },
    { hip: 65378, chinese: '开阳', english: 'Mizar', constellation: '大熊座', bayer: 'ζ UMa' },
    { hip: 67301, chinese: '瑶光', english: 'Alkaid', constellation: '大熊座', bayer: 'η UMa' },
    
    // 仙后座主要星
    { hip: 3179, chinese: '王良一', english: 'Schedar', constellation: '仙后座', bayer: 'α Cas' },
    { hip: 746, chinese: '王良四', english: 'Caph', constellation: '仙后座', bayer: 'β Cas' },
    
    // 天鹰座三星
    { hip: 95947, chinese: '河鼓一', english: 'Tarazed', constellation: '天鹰座', bayer: 'γ Aql' },
    { hip: 98036, chinese: '河鼓三', english: 'Alshain', constellation: '天鹰座', bayer: 'β Aql' },
    
    // 南船五
    { hip: 45238, chinese: '南船五', english: 'Naos', constellation: '船尾座', bayer: 'ζ Pup' },
    
    // 其他亮星
    { hip: 677, chinese: '土司空', english: 'Alpheratz', constellation: '仙女座', bayer: 'α And' },
    { hip: 15863, chinese: '五车三', english: 'Menkalinan', constellation: '御夫座', bayer: 'β Aur' },
    { hip: 113881, chinese: '垒壁阵四', english: 'Ankaa', constellation: '凤凰座', bayer: 'α Phe' },
    { hip: 9884, chinese: '天仓五', english: 'Mirach', constellation: '仙女座', bayer: 'β And' },
    { hip: 17702, chinese: '昴宿六', english: 'Alcyone', constellation: '金牛座', bayer: 'η Tau' },
];

// 创建快速查找映射
export const starNameMap = new Map<number, StarName>(
    BRIGHT_STAR_NAMES.map(star => [star.hip, star])
);

/**
 * 根据HIP编号获取星星名称
 */
export function getStarName(hip: number): StarName | undefined {
    return starNameMap.get(hip);
}

/**
 * 格式化星星显示名称
 */
export function formatStarDisplayName(hip: number): string {
    const starName = getStarName(hip);
    if (starName) {
        return `${starName.chinese} (${starName.english})`;
    }
    return `HIP ${hip}`;
}
