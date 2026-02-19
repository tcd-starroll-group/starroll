import { PlanetConfig } from '../../types/planet';

// 为了可视化效果，这里的数据并非真实比例，而是经过艺术调整的“可视化比例”
// 真实比例下，行星相对于轨道太小，几乎看不见。
export const solarSystemData: PlanetConfig[] = [
    {
        id: 'sun',
        name: '太阳',
        type: 'star',
        radius: 25,
        orbitRadius: 0,
        orbitPeriod: 1,
        rotationPeriod: 25,
        color: 0xffaa00,
        visual: { emissive: true }
    },
    {
        id: 'mercury',
        name: '水星',
        type: 'planet',
        radius: 2,
        orbitRadius: 60,
        orbitPeriod: 0.24,
        rotationPeriod: 58,
        color: 0xa1a1a1, // 灰白色
        visual: {
            noiseScale: 3.0, // 岩石表面，中等噪声
            noiseStrength: 0.15,
            rimPower: 4.0 // 大气极其稀薄，边缘光弱
        }
    },
    {
        id: 'venus',
        name: '金星',
        type: 'planet',
        radius: 3,
        orbitRadius: 90,
        orbitPeriod: 0.61,
        rotationPeriod: -243, // 逆向自转
        color: 0xe6c288, // 浓厚大气，金黄色
        visual: {
            noiseScale: 0.5, // 巨大的大气云层，噪声缩放小
            noiseStrength: 0.1,
            rimPower: 2.0 // 大气浓厚，边缘光柔和
        }
    },
    {
        id: 'earth',
        name: '地球',
        type: 'planet',
        radius: 3.2,
        orbitRadius: 130,
        orbitPeriod: 1.0,
        rotationPeriod: 1,
        color: 0x2255ff, // 蓝色 (实际会混入 Shader 噪声)
        visual: {
            noiseScale: 1.2, // 模拟云层和大陆
            noiseStrength: 0.2,
            rimPower: 2.5 // 明显的蓝色大气层
        }
    },
    {
        id: 'mars',
        name: '火星',
        type: 'planet',
        radius: 1.8,
        orbitRadius: 170,
        orbitPeriod: 1.88,
        rotationPeriod: 1.03,
        color: 0xff4422, // 锈红色
        visual: {
            noiseScale: 3.5, // 粗糙岩石地表
            noiseStrength: 0.25,
            rimPower: 3.5 // 稀薄大气
        }
    },
    {
        id: 'jupiter',
        name: '木星',
        type: 'planet',
        radius: 12,
        orbitRadius: 260,
        orbitPeriod: 11.86,
        rotationPeriod: 0.41,
        color: 0xc9b584, // 棕黄色
        hasRings: true, 
        ringConfig: {
            innerRadius: 14,
            outerRadius: 20,
            color: 0xaa9977,
            count: 5000 // 增加粒子数
        },
        visual: {
            noiseScale: 0.3, 
            noiseStrength: 0.3
        }
    },
    {
        id: 'saturn',
        name: '土星',
        type: 'planet',
        radius: 10,
        orbitRadius: 360,
        orbitPeriod: 29.46,
        rotationPeriod: 0.44,
        color: 0xf0d080, // 淡黄色
        hasRings: true,
        ringConfig: {
            innerRadius: 14,
            outerRadius: 30, // 稍微加宽
            color: 0xcfb096, 
            count: 50000 // 大幅增加粒子数 (50k)
        },
        visual: {
            noiseScale: 0.4,
            noiseStrength: 0.2
        }
    },
    {
        id: 'uranus',
        name: '天王星',
        type: 'planet',
        radius: 6,
        orbitRadius: 480,
        orbitPeriod: 84,
        rotationPeriod: -0.72,
        color: 0x88ffff, // 青色
        hasRings: true,
        ringConfig: {
            innerRadius: 9,
            outerRadius: 13,
            color: 0xccffff, // 稍微调亮光环颜色
            count: 4000
        },
        visual: {
            noiseScale: 0.2, 
            noiseStrength: 0.1
        }
    },
    {
        id: 'neptune',
        name: '海王星',
        type: 'planet',
        radius: 6,
        orbitRadius: 600,
        orbitPeriod: 164.8,
        rotationPeriod: 0.67,
        color: 0x3366ff, // 深蓝色
        hasRings: true, 
        ringConfig: {
            innerRadius: 9,
            outerRadius: 14,
            color: 0x88aaff, // 调亮
            count: 3000
        },
        visual: {
            noiseScale: 0.25,
            noiseStrength: 0.15,
            rimPower: 2.0
        }
    }
];
