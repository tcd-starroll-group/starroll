import * as THREE from 'three';

// --- GLSL 工具库 (Noise + Math) ---
const COMMON_CHUNK = `
// Simplex 3D Noise
vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x, 289.0);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}

float snoise(vec3 v){ 
  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 = v - i + dot(i, C.xxx) ;
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );
  vec3 x1 = x0 - i1 + 1.0 * C.xxx;
  vec3 x2 = x0 - i2 + 2.0 * C.xxx;
  vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;
  i = mod(i, 289.0 ); 
  vec4 p = permute( permute( permute( 
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
  float n_ = 1.0/7.0; 
  vec3  ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z *ns.z); 
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ ); 
  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x; p1 *= norm.y; p2 *= norm.z; p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
}

// Fractal Brownian Motion
float fbm(vec3 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 5; i++) {
        value += amplitude * snoise(p * frequency);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

// Domain Warping (用噪声扭曲坐标)
float warp(vec3 p) {
    vec3 q = vec3(
        fbm(p + vec3(0.0, 0.0, 0.0)),
        fbm(p + vec3(5.2, 1.3, 2.8)),
        fbm(p + vec3(1.1, 4.4, 3.2))
    );
    return fbm(p + 4.0 * q);
}
`;

// 基础顶点 Shader (通用)
const BASE_VERTEX = `
varying vec3 vWorldPosition;
void main() {
    vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

import { createDeepPurpleNebula } from './NebulaShaderPurple';

export type NebulaType = 'spiral' | 'filament' | 'explosive' | 'layered' | 'dark' | 'milky' | 'purple' | 'deepspace';

// 导出新的函数以便 GalaxyBackgroundRenderer 使用
export { 
    createDeepPurpleNebula
};

/**
 * 1. 螺旋星云 (Spiral Nebula)
 * 原理：通过极坐标旋转扭曲 UV 采样，模拟旋转吸积盘
 */
export function createSpiralNebula() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0x000510) }, // 深黑蓝
            uColorB: { value: new THREE.Color(0x2a0044) }, // 紫
            uColorC: { value: new THREE.Color(0xffaa00) }, // 核心橙
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            uniform vec3 uColorC;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 极坐标转换 (简化版：投影到 XZ 平面)
                float angle = atan(p.z, p.x);
                float dist = length(p.xz);
                
                // 旋转扭曲：随距离增加旋转角度
                float spiralAngle = angle + dist * 5.0 - uTime * 0.1;
                
                vec3 spiralP = vec3(cos(spiralAngle)*dist, p.y, sin(spiralAngle)*dist);
                
                // 噪声采样
                float n = fbm(spiralP * 3.0);
                
                // 核心区域
                float core = 1.0 - abs(p.y); // 赤道面亮
                core = pow(core, 4.0);
                
                vec3 color = mix(uColorA, uColorB, n * 0.5 + 0.5);
                color = mix(color, uColorC, core * (n * 0.5 + 0.5));
                
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 2. 丝状星云 (Filament Nebula)
 * 原理：强 Domain Warping，制造拉丝感
 */
export function createFilamentNebula() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0x001133) }, // 深蓝
            uColorB: { value: new THREE.Color(0x00ffff) }, // 青色
            uColorC: { value: new THREE.Color(0xffffff) }, // 白
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            uniform vec3 uColorC;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 强烈的域翘曲
                // 时间参与 warp
                float n = warp(p * 2.0 + vec3(uTime * 0.05));
                
                // 锐化噪声，突出丝状
                float filament = smoothstep(0.4, 0.6, n);
                
                vec3 color = mix(uColorA, uColorB, n);
                color += uColorC * filament * 0.5;
                
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 3. 爆炸星云 (Explosive Nebula)
 * 原理：从中心向外辐射的冲击波纹理
 */
export function createExplosiveNebula() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0x220000) }, // 暗红
            uColorB: { value: new THREE.Color(0xff3300) }, // 烈火红
            uColorC: { value: new THREE.Color(0xffaa00) }, // 金黄
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            uniform vec3 uColorC;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 基础 FBM
                float n = fbm(p * 4.0 - vec3(uTime * 0.1));
                
                // 冲击波纹：叠加正弦波
                float wave = sin(length(p) * 20.0 - uTime); // 这里 length(p) 总是 1 因为 normalize 了...
                // 实际上背景球很大，p 是方向。我们需要一种假的空间感。
                // 我们可以用 noise 值本身做波纹
                
                float fire = n * n * n; // 增加对比度，像火焰
                
                vec3 color = mix(uColorA, uColorB, n);
                color = mix(color, uColorC, fire * 2.0);
                
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 4. 多层星云 (Layered Nebula)
 * 原理：通过 Y 轴分层，每一层不同的颜色和噪声频率
 */
export function createLayeredNebula() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0x0a0a0a) }, // 黑
            uColorB: { value: new THREE.Color(0x442288) }, // 紫层
            uColorC: { value: new THREE.Color(0x228888) }, // 青层
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            uniform vec3 uColorC;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 基于高度 Y 的分层
                float y = p.y * 5.0 + fbm(p * 2.0 + uTime*0.05); // 扭曲的层
                
                float layer1 = smoothstep(0.2, 0.8, sin(y));
                float layer2 = smoothstep(0.2, 0.8, cos(y * 0.5));
                
                vec3 color = uColorA;
                color = mix(color, uColorB, layer1);
                color = mix(color, uColorC, layer2 * 0.5);
                
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 5. 黑暗星云 (Dark Nebula)
 * 原理：明亮的背景上覆盖黑色的吸收云
 */
export function createDarkNebula() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0x666666) }, // 背景灰亮
            uColorB: { value: new THREE.Color(0x000000) }, // 黑暗吸收云
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 浓密的噪声云
                float n = fbm(p * 3.0 + vec3(uTime * 0.02));
                
                // 阈值切割：只有最浓的地方是黑色
                float mask = smoothstep(0.4, 0.7, n);
                
                // 背景稍微带点星光感
                float stars = pow(fbm(p * 20.0), 10.0) * 0.5;
                
                vec3 bg = uColorA + stars;
                vec3 color = mix(bg, uColorB, mask * 0.95); // 不完全黑，稍微透一点
                
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 6. 深空网格 (Deep Space Grid)
 * 原理：极暗背景 + 稀疏紫雾 + 程序化网格线
 */
export function createDeepSpaceGrid() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorBg: { value: new THREE.Color(0x050508) }, // 极深黑蓝
            uColorMist: { value: new THREE.Color(0x2a0a44) }, // 暗紫雾
            uColorGrid: { value: new THREE.Color(0x222233) }, // 极其暗淡的网格色
        },
        vertexShader: BASE_VERTEX,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorBg;
            uniform vec3 uColorMist;
            uniform vec3 uColorGrid;
            varying vec3 vWorldPosition;
            
            ${COMMON_CHUNK}

            void main() {
                vec3 p = normalize(vWorldPosition);
                
                // 1. 背景：深空黑
                vec3 color = uColorBg;
                
                // 2. 稀疏紫雾：只在局部出现
                // 使用低频噪声，并设定高阈值，只保留少量团块
                float n = fbm(p * 1.5 + vec3(uTime * 0.01));
                float mistMask = smoothstep(0.6, 0.9, n); // 只有噪声值 > 0.6 的地方才有雾
                
                color += uColorMist * mistMask * 0.8;
                
                // 3. 程序化网格 (Grid / Orbit Lines)
                // 在 XZ 平面上画同心圆
                // 计算 p 在 XZ 平面上的投影长度 (0 ~ 1)
                float dist = length(p.xz);
                float y = abs(p.y);
                
                // 只有在赤道面附近才显示网格，避免极点变形太难看
                float gridFade = smoothstep(0.5, 0.0, y); // 越靠近赤道越清楚
                
                if (gridFade > 0.01) {
                    // 同心圆：基于 dist 的正弦波
                    float rings = sin(dist * 80.0); // 密度
                    // 锐化成线
                    float ringLine = smoothstep(0.95, 0.98, rings);
                    
                    // 径向线
                    float angle = atan(p.z, p.x);
                    float radials = sin(angle * 20.0);
                    float radialLine = smoothstep(0.98, 0.99, radials);
                    
                    float grid = max(ringLine, radialLine);
                    
                    // 叠加网格：非常暗淡，且随 Y 轴淡出
                    color += uColorGrid * grid * gridFade * 0.15; // 0.15 强度
                }

                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}
