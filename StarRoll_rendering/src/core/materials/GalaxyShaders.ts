import * as THREE from 'three';

// --- Noise Functions Chunk ---
// 包含 Simplex Noise 和 FBM
const noiseChunk = `
// Simplex 3D Noise 
// by Ian McEwan, Ashima Arts
vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x, 289.0);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}

float snoise(vec3 v){ 
  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);

  // First corner
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 = v - i + dot(i, C.xxx) ;

  // Other corners
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );

  //  x0 = x0 - 0.0 + 0.0 * C 
  vec3 x1 = x0 - i1 + 1.0 * C.xxx;
  vec3 x2 = x0 - i2 + 2.0 * C.xxx;
  vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;

  // Permutations
  i = mod(i, 289.0 ); 
  vec4 p = permute( permute( permute( 
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));

  // Gradients
  // ( N*N points uniformly over a square, mapped onto an octahedron.)
  float n_ = 1.0/7.0; // N=7
  vec3  ns = n_ * D.wyz - D.xzx;

  vec4 j = p - 49.0 * floor(p * ns.z *ns.z);  //  mod(p,N*N)

  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );    // mod(j,N)

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

  //Normalise gradients
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;

  // Mix final noise value
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), 
                                dot(p2,x2), dot(p3,x3) ) );
}

// Fractal Brownian Motion (FBM)
// 叠加多层噪声，创造云雾感
float fbm(vec3 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    // 叠加 5 层
    for (int i = 0; i < 5; i++) {
        value += amplitude * snoise(p * frequency);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value; // Range approx -1.0 to 1.0
}
`;

/**
 * 1. 程序化星云背景材质
 * 用于渲染包裹整个场景的巨大天空球
 */
export function createNebulaMaterial() {
    return new THREE.ShaderMaterial({
        side: THREE.BackSide, // 渲染球体内表面
        depthWrite: false, // 作为背景，不写入深度
        uniforms: {
            uTime: { value: 0 },
            uColorDeep: { value: new THREE.Color(0x0a0f2f) }, // 深蓝
            uColorMid: { value: new THREE.Color(0x4c2a85) },  // 紫色
            uColorLite: { value: new THREE.Color(0xa862af) }, // 星云粉(低饱和)
            uGalaxyDir: { value: new THREE.Vector3(1.0, 0.4, 0.2).normalize() } // 银河带方向
        },
        vertexShader: `
            varying vec3 vWorldPosition;
            varying vec3 vViewDirection;
            
            void main() {
                // 计算世界坐标，用于噪声采样 (不受模型旋转影响，或者跟随天空盒旋转)
                vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
                
                // 简单的天空盒投影
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorDeep;
            uniform vec3 uColorMid;
            uniform vec3 uColorLite;
            uniform vec3 uGalaxyDir;
            
            varying vec3 vWorldPosition;
            
            ${noiseChunk}

            void main() {
                // 归一化方向向量
                vec3 dir = normalize(vWorldPosition);
                
                // 1. 基础 FBM 噪声生成云雾纹理
                // 缓慢移动 uTime
                float n = fbm(dir * 2.0 + vec3(0.0, uTime * 0.02, 0.0));
                
                // 2. 银河带计算
                // 计算当前方向与银河轴线的距离 (点积绝对值越小，越垂直于轴线 -> 可以在赤道面上，也可以设定特定平面)
                // 这里我们假设银河集中在 uGalaxyDir 定义的“赤道”平面附近
                // 即 dot(dir, uGalaxyDir) 接近 0 的地方
                float galaxyIntensity = 1.0 - abs(dot(dir, uGalaxyDir));
                galaxyIntensity = pow(galaxyIntensity, 4.0); // 锐化，使其集中在带状区域
                
                // 叠加噪声到银河带：让银河带看起来不是均匀的，而是絮状的
                float galaxyNoise = fbm(dir * 5.0 - vec3(uTime * 0.01));
                float galaxyFinal = galaxyIntensity * (0.5 + 0.5 * galaxyNoise);
                
                // 3. 颜色混合
                // 基础色：深空黑蓝
                vec3 color = uColorDeep;
                
                // 混合中层紫色 (基于全域噪声 n)
                // n 范围约 -1~1，归一化到 0~1
                float nNorm = n * 0.5 + 0.5; 
                color = mix(color, uColorMid, nNorm * 0.4); // 淡淡的紫色云气
                
                // 混合亮部 (银河带 + 高亮噪声)
                // 在银河带区域，叠加亮粉色
                color = mix(color, uColorLite, galaxyFinal * 0.8);
                
                // 增加一点极亮核心 (伪恒星密集区)
                float core = smoothstep(0.6, 1.0, galaxyFinal + nNorm * 0.2);
                color += vec3(0.2, 0.1, 0.1) * core;

                // 最终输出
                // 稍微降低整体亮度，作为背景不应抢眼
                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 2. 闪烁星点材质
 * 用于 BufferGeometry Points，模拟成千上万的恒星
 */
export function createTwinkleStarMaterial() {
    return new THREE.ShaderMaterial({
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        uniforms: {
            uTime: { value: 0 },
            uBaseSize: { value: 3.0 }, // 基础大小
            uColor: { value: new THREE.Color(0xffffff) }
        },
        vertexShader: `
            uniform float uTime;
            uniform float uBaseSize;
            
            attribute float aSize;   // 每个星星的固有大小
            attribute float aPhase;  // 闪烁相位偏移 (随机数 0~2PI)
            attribute float aSpeed;  // 闪烁速度 (随机数)
            attribute vec3 aColor;   // 星星颜色
            
            varying vec3 vColor;
            varying float vAlpha;
            
            void main() {
                vColor = aColor;
                
                // 闪烁逻辑:基于 sin 波
                float twinkle = 0.5 + 0.5 * sin(uTime * aSpeed + aPhase);
                // 稍微限制最小值，不要完全消失
                twinkle = mix(0.3, 1.0, twinkle);
                
                vAlpha = twinkle;
                
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                gl_Position = projectionMatrix * mvPosition;
                
                // 距离衰减
                // 越远的星星越小
                gl_PointSize = uBaseSize * aSize * (300.0 / -mvPosition.z);
            }
        `,
        fragmentShader: `
            varying vec3 vColor;
            varying float vAlpha;
            
            void main() {
                // 简单的圆形粒子
                vec2 uv = gl_PointCoord.xy - 0.5;
                float r = length(uv);
                if (r > 0.5) discard;
                
                // 边缘羽化
                float glow = 1.0 - (r * 2.0);
                glow = pow(glow, 2.0);
                
                gl_FragColor = vec4(vColor, glow * vAlpha);
            }
        `
    });
}

