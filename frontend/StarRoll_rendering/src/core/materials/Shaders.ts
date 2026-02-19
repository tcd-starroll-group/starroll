import * as THREE from 'three';

// --- 基础噪声函数 Chunk (Simplex Noise + FBM) ---
// 我们扩充 noiseChunk，加入 FBM (分形布朗运动) 以获得更丰富的细节
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

// FBM (Fractal Brownian Motion)
// 叠加多层噪声，每层频率翻倍、振幅减半
float fbm(vec3 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 4; i++) {
        value += amplitude * snoise(p * frequency);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}
`;

/**
 * 创建行星表面材质 (Procedural Planet Material)
 * 升级版：加入真实光照计算 + FBM 复杂噪声
 */
export interface PlanetMaterialOptions {
    color: THREE.ColorRepresentation;
    noiseScale?: number;
    noiseStrength?: number;
    rimPower?: number;
}

export function createPlanetMaterial(options: PlanetMaterialOptions) {
    const baseColor = new THREE.Color(options.color);
    const noiseScale = options.noiseScale ?? 2.0;
    const noiseStrength = options.noiseStrength ?? 0.1;
    const rimPower = options.rimPower ?? 3.0;
    
    return new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uBaseColor: { value: baseColor },
            uSunPosition: { value: new THREE.Vector3(0, 0, 0) }, // 太阳位置
            uRimColor: { value: new THREE.Color(0x44aaff) },
            uRimPower: { value: rimPower },
            uNoiseScale: { value: noiseScale },
            uNoiseStrength: { value: noiseStrength }
        },
        vertexShader: `
            varying vec3 vNormal;
            varying vec3 vPosition;
            varying vec2 vUv;
            
            void main() {
                vNormal = normalize(normalMatrix * normal);
                vPosition = (modelMatrix * vec4(position, 1.0)).xyz;
                vUv = uv;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform vec3 uBaseColor;
            uniform vec3 uSunPosition; // 世界空间下的太阳位置
            uniform vec3 uRimColor;
            uniform float uRimPower;
            uniform float uTime;
            uniform float uNoiseScale;
            uniform float uNoiseStrength;
            
            varying vec3 vNormal;
            varying vec3 vPosition;
            varying vec2 vUv;
            
            ${noiseChunk}

            void main() {
                // 1. 计算光照方向
                // 光线从太阳射向行星点 vPosition，所以 lightDir 是 normalize(sunPos - vPos)
                vec3 sunPos = uSunPosition;
                vec3 lightDir = normalize(sunPos - vPosition);
                vec3 viewDir = normalize(cameraPosition - vPosition); // Three.js 内置 cameraPosition
                vec3 normal = normalize(vNormal);

                // 2. 漫反射 (Lambert) - 模拟昼夜
                // 只有面向太阳的一面会被照亮
                float diff = max(dot(normal, lightDir), 0.0);
                
                // 增加一点环境光，防止背面全黑
                float ambient = 0.05; 

                // 3. FBM 噪声生成复杂地表/大气纹理
                // 使用世界坐标采样，避免 UV 接缝问题，并让纹理随自转自然移动 (因 vPos 随模型旋转)
                // 这里的 vPos 是世界坐标。如果模型旋转，vPos 也会变。
                // 气态行星通常有流动的云层：加上 uTime
                float n = fbm(vPosition * uNoiseScale + vec3(0.0, uTime * 0.05, 0.0));
                
                // 将噪声映射到 [-1, 1] 之外更丰富的范围，增加对比度
                float noiseFactor = n * uNoiseStrength;
                
                // 混合颜色：在亮部和暗部之间通过噪声扰动
                vec3 surfaceColor = uBaseColor * (1.0 + noiseFactor);

                // 4. 合成光照
                vec3 finalColor = surfaceColor * (diff + ambient);

                // 5. 科幻边缘光 (Rim Light)
                // Rim Light 通常模拟大气层散射。
                // 我们希望在受光面的边缘（地平线）最亮，背光面也可以有一点微弱辉光
                float rim = 1.0 - abs(dot(normal, viewDir));
                rim = pow(rim, uRimPower);
                
                // 让边缘光也受一点光照方向影响 (面向太阳的那一边大气更亮)
                // 或者保持全方位发光模拟厚重大气
                // 这里我们做全方位，但在背光面稍微暗一点
                float sunFactor = max(dot(lightDir, viewDir), 0.0) * 0.5 + 0.5;
                
                finalColor += uRimColor * rim * sunFactor * 0.8;

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    });
}

/**
 * 创建太阳材质 (Emissive + Dynamic FBM)
 */
export function createSunMaterial() {
    return new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uColorA: { value: new THREE.Color(0xffaa00) }, // 橙色
            uColorB: { value: new THREE.Color(0xff4400) }, // 红色
        },
        vertexShader: `
            varying vec3 vPosition;
            varying vec3 vNormal;
            void main() {
                vPosition = position;
                vNormal = normalize(normalMatrix * normal);
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorA;
            uniform vec3 uColorB;
            
            varying vec3 vPosition;
            varying vec3 vNormal;
            
            ${noiseChunk}

            void main() {
                // 动态湍流噪声 FBM
                float n = fbm(vPosition * 0.8 + vec3(0.0, uTime * 0.2, 0.0));
                
                // 太阳耀斑感的颜色混合
                vec3 color = mix(uColorA, uColorB, n * 0.6 + 0.4);
                
                // 中心亮度更高 (简单模拟)
                float core = dot(normalize(vNormal), vec3(0.0, 0.0, 1.0)); 
                color += vec3(0.1) * max(core, 0.0);

                // 极亮核心
                color *= 1.2;

                gl_FragColor = vec4(color, 1.0);
            }
        `
    });
}

/**
 * 创建星空粒子材质 (用于光环或背景)
 * 升级版：更锐利、更亮的晶体感
 */
export function createStarPointMaterial(color: THREE.ColorRepresentation = 0xffffff) {
    return new THREE.ShaderMaterial({
        uniforms: {
            uTime: { value: 0 },
            uColor: { value: new THREE.Color(color) },
            uSize: { value: 4.0 }, 
        },
        transparent: true,
        depthWrite: false, 
        blending: THREE.AdditiveBlending,
        vertexShader: `
            uniform float uSize;
            attribute float aScale; 
            varying float vAlpha;
            
            void main() {
                vAlpha = aScale; 
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                gl_Position = projectionMatrix * mvPosition;
                
                // 距离衰减：离相机越远越小
                gl_PointSize = uSize * (300.0 / -mvPosition.z) * aScale;
            }
        `,
        fragmentShader: `
            uniform vec3 uColor;
            varying float vAlpha;
            
            void main() {
                // 更锐利的粒子形状 (模拟冰晶反光)
                vec2 uv = gl_PointCoord.xy - 0.5;
                float dist = length(uv);
                if (dist > 0.5) discard;

                // 核心极亮，边缘迅速衰减
                // 0.0 ~ 0.5 -> 1.0 ~ 0.0
                float strength = 1.0 - (dist * 2.0); 
                strength = pow(strength, 2.0); // 降低衰减次幂，让粒子看起来更饱满更亮 (原本是 3.0)

                // 增加基础亮度乘数
                gl_FragColor = vec4(uColor, strength * vAlpha * 1.5);
            }
        `
    });
}
