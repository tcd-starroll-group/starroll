import type { ConstellationLines } from '../../types/star-meta';

/**
 * 星座 3D 模型配置
 * 将星座 ID 映射到 GLTF 模型文件
 */
export interface ConstellationModel {
    id: string;
    name: string;
    modelPath: string;
    centerHIP?: number;  // 用于定位模型的中心恒星 HIP 编号
    scale?: number;      // 模型缩放比例
}

/**
 * 星座模型配置列表
 */
export const constellationModels: ConstellationModel[] = [
    {
        id: 'AND',
        name: '仙女座 Andromeda',
        modelPath: '/models/andromeda-constellation.gltf',
        centerHIP: 3092,  // Mirach (仙女座β)
        scale: 50
    },
    {
        id: 'AQR',
        name: '水瓶座 Aquarius',
        modelPath: '/models/aquarius-constellation.gltf',
        centerHIP: 110960,  // Sadalsuud (虚宿一)
        scale: 50
    },
    {
        id: 'AQL',
        name: '天鹰座 Aquila',
        modelPath: '/models/aquila-constellation.gltf',
        centerHIP: 97649,  // Altair (河鼓二/牛郎星)
        scale: 50
    },
    {
        id: 'ARI',
        name: '白羊座 Aries',
        modelPath: '/models/aries-constellation.gltf',
        centerHIP: 9884,  // Hamal (娄宿三)
        scale: 50
    },
    {
        id: 'CVN',
        name: '猎犬座 Canes Venatici',
        modelPath: '/models/canes-venatici.gltf',
        centerHIP: 63125,  // Cor Caroli (常陈一)
        scale: 50
    },
    {
        id: 'CAS',
        name: '仙后座 Cassiopeia',
        modelPath: '/models/cassiopeia-constellation.gltf',
        centerHIP: 3179,  // Schedar (王良一)
        scale: 50
    },
    {
        id: 'CYG',
        name: '天鹅座 Cygnus',
        modelPath: '/models/cygnus-constellation.gltf',
        centerHIP: 102098,  // Deneb (天津四)
        scale: 50
    },
    {
        id: 'GEM',
        name: '双子座 Gemini',
        modelPath: '/models/gemini-constellation.gltf',
        centerHIP: 37826,  // Pollux (北河三)
        scale: 50
    },
    {
        id: 'LYN',
        name: '天猫座 Lynx',
        modelPath: '/models/lynx-constellation.gltf',
        centerHIP: 45860,  // α Lyncis
        scale: 50
    },
    {
        id: 'PEG',
        name: '飞马座 Pegasus',
        modelPath: '/models/pegasus-constellation.gltf',
        centerHIP: 113881,  // Enif (室宿一)
        scale: 50
    }
];

/**
 * 扩展的星座连线定义（包含已有模型的星座）
 */
export const constellationLinesWithModels: ConstellationLines[] = [
    {
        id: 'AND',
        name: '仙女座 Andromeda',
        lines: [
            [677, 3092],      // Alpheratz - Mirach
            [3092, 5447],     // Mirach - Almach
            [3092, 4436],     // Mirach - δ And
        ]
    },
    {
        id: 'AQR',
        name: '水瓶座 Aquarius',
        lines: [
            [110960, 109074], // Sadalsuud - Sadalmelik
            [109074, 113136], // Sadalmelik - λ Aqr
            [106278, 110960], // δ Aqr - Sadalsuud
        ]
    },
    {
        id: 'AQL',
        name: '天鹰座 Aquila',
        lines: [
            [97649, 95947],   // Altair - Tarazed
            [97649, 97804],   // Altair - Alshain
            [95947, 93747],   // Tarazed - ζ Aql
        ]
    },
    {
        id: 'ARI',
        name: '白羊座 Aries',
        lines: [
            [9884, 8903],     // Hamal - Sheratan
            [8903, 8832],     // Sheratan - Mesarthim
        ]
    },
    {
        id: 'CAS',
        name: '仙后座 Cassiopeia',
        lines: [
            [746, 3179],      // α Cas - Schedar
            [3179, 4427],     // Schedar - γ Cas
            [4427, 6686],     // γ Cas - δ Cas
            [6686, 8886],     // δ Cas - ε Cas
        ]
    },
    {
        id: 'CYG',
        name: '天鹅座 Cygnus',
        lines: [
            [102098, 100453], // Deneb - Sadr
            [100453, 95947],  // Sadr - Albireo
            [104732, 100453], // δ Cyg - Sadr
            [94779, 100453],  // ε Cyg - Sadr
        ]
    },
    {
        id: 'GEM',
        name: '双子座 Gemini',
        lines: [
            [37826, 36850],   // Pollux - Castor
            [37826, 34693],   // Pollux - Alhena
            [36850, 32362],   // Castor - μ Gem
            [34693, 31681],   // Alhena - δ Gem
        ]
    },
    {
        id: 'PEG',
        name: '飞马座 Pegasus',
        lines: [
            [677, 113881],    // Alpheratz - Enif
            [677, 1067],      // Alpheratz - Scheat
            [1067, 112029],   // Scheat - Markab
            [112029, 113963], // Markab - Algenib
            [113963, 677],    // Algenib - Alpheratz (形成方形)
        ]
    }
];

/**
 * 根据星座 ID 获取模型配置
 */
export function getConstellationModel(id: string): ConstellationModel | undefined {
    return constellationModels.find(model => model.id === id);
}

/**
 * 获取所有有模型的星座 ID
 */
export function getConstellationIdsWithModels(): string[] {
    return constellationModels.map(model => model.id);
}
