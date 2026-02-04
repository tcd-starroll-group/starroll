import { ConstellationData } from '../../types/constellation';

// 示例数据：猎户座 (Orion) 和 天鹅座 (Cygnus)
export const sampleConstellations: ConstellationData[] = [
    {
        id: 'ORI',
        name: { en: 'Orion', zh: '猎户座' },
        description: '猎户座是冬季夜空中最壮丽的星座，腰带三颗星清晰可见。',
        shapeId: 'human',
        center: { ra: 83, dec: 0 }, // 大概中心
        stars: [
            { id: 0, ra: 88.79, dec: 7.4, mag: 0.45 }, // Betelgeuse (参宿四)
            { id: 1, ra: 78.63, dec: -8.2, mag: 0.18 }, // Rigel (参宿七)
            { id: 2, ra: 81.28, dec: 6.34, mag: 1.64 }, // Bellatrix (参宿五)
            { id: 3, ra: 83.00, dec: -0.29, mag: 2.25 }, // Mintaka (参宿三 - 腰带)
            { id: 4, ra: 84.05, dec: -1.20, mag: 1.69 }, // Alnilam (参宿二 - 腰带)
            { id: 5, ra: 85.19, dec: -1.94, mag: 1.74 }, // Alnitak (参宿一 - 腰带)
            { id: 6, ra: 86.93, dec: -9.66, mag: 2.07 }, // Saiph (参宿六)
        ],
        lines: [
            [0, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 1], [1, 5], [3, 0], // 简化连线
            [3, 5] // 腰带
        ]
    },
    {
        id: 'CYG',
        name: { en: 'Cygnus', zh: '天鹅座' },
        description: '天鹅座位于银河之中，形状像一只飞翔的天鹅，也就是北十字。',
        shapeId: 'bird',
        center: { ra: 305, dec: 45 },
        stars: [
            { id: 0, ra: 310.3, dec: 45.28, mag: 1.25 }, // Deneb (天津四)
            { id: 1, ra: 297.0, dec: 27.9, mag: 3.0 }, // Albireo (辇道增七 - 头部)
            { id: 2, ra: 306.0, dec: 33.9, mag: 2.2 }, // Sadr (天津一 - 胸部)
            { id: 3, ra: 315.0, dec: 30.0, mag: 2.5 }, // 翅膀左
            { id: 4, ra: 290.0, dec: 51.0, mag: 2.8 }, // 翅膀右
        ],
        lines: [
            [0, 2], [2, 1], // 身体轴线
            [3, 2], [2, 4]  // 翅膀横线
        ]
    }
];

