import * as THREE from 'three';

// 复用之前的噪声库，但这里我们只需要基础 Simplex Noise
const NOISE_CHUNK = `
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

// 简单的多层噪声 (FBM)，频率低一点，更柔和
float softFbm(vec3 p) {
    float v = 0.0;
    float a = 0.5;
    // 只叠3层，保证平滑
    for(int i=0; i<3; i++){
        v += a * snoise(p);
        p *= 2.0;
        a *= 0.5;
    }
    return v;
}
`;

/**
 * 创建深邃紫雾星云材质
 */
export function createDeepPurpleNebula() {
    // 定义多个星云中心方向 (单位向量)
    // 前、后、左上、右下等不同方位
    const centers = [
        new THREE.Vector3(1, 0.2, -0.5).normalize(),
        new THREE.Vector3(-0.8, 0.5, 0.2).normalize(),
        new THREE.Vector3(0.2, -0.8, 0.6).normalize()
    ];

    return new THREE.ShaderMaterial({
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: {
            uTime: { value: 0 },
            uColorDeep: { value: new THREE.Color(0x2d0a3f) }, // 深紫
            uColorMid: { value: new THREE.Color(0x3a1766) },  // 暗紫
            uColorLite: { value: new THREE.Color(0xb36bff) }, // 柔亮紫
            uCenters: { value: centers } // 传入中心点数组
        },
        vertexShader: `
            varying vec3 vWorldPosition;
            void main() {
                vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
                gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
            }
        `,
        fragmentShader: `
            uniform float uTime;
            uniform vec3 uColorDeep;
            uniform vec3 uColorMid;
            uniform vec3 uColorLite;
            uniform vec3 uCenters[3]; // 3个星云团
            
            varying vec3 vWorldPosition;
            
            ${NOISE_CHUNK}

            void main() {
                vec3 dir = normalize(vWorldPosition);
                
                // 基础背景色 (极暗的深紫黑)
                vec3 finalColor = vec3(0.02, 0.01, 0.05);
                
                // 遍历每个星云中心，累加星云亮度
                float totalNebula = 0.0;
                
                for(int i=0; i<3; i++) {
                    vec3 center = uCenters[i];
                    
                    // 1. 距离衰减：计算视线与中心的夹角余弦
                    float dist = dot(dir, center); 
                    // dist 范围 -1 ~ 1。我们只关心 > 0 的部分 (面向中心)
                    // 使用 smoothstep 让边缘柔和
                    float mask = smoothstep(0.4, 1.0, dist);
                    
                    if (mask > 0.01) {
                        // 2. 内部纹理：基于 FBM
                        // 不同的中心用不同的 offset 采样，避免长得一样
                        vec3 p = dir * 2.0 + vec3(float(i)*10.0);
                        // 加入时间流动
                        p += vec3(0.0, uTime * 0.03, 0.0);
                        
                        float n = softFbm(p); // Range -1 ~ 1
                        n = n * 0.5 + 0.5;    // Range 0 ~ 1
                        
                        // 结合 mask 和 noise
                        // mask 决定大轮廓，n 决定内部云气
                        float strength = mask * n;
                        
                        // 累加到总亮度
                        totalNebula += strength;
                    }
                }
                
                // 限制最大亮度
                totalNebula = clamp(totalNebula, 0.0, 1.2);
                
                // 3. 颜色映射
                // 根据亮度混合三层颜色
                // 0.0 ~ 0.4 -> Deep
                // 0.4 ~ 0.7 -> Mid
                // 0.7 ~ 1.0 -> Lite
                
                vec3 nebulaColor = mix(uColorDeep, uColorMid, smoothstep(0.0, 0.5, totalNebula));
                nebulaColor = mix(nebulaColor, uColorLite, smoothstep(0.5, 1.0, totalNebula));
                
                // 将星云叠加到背景上
                // 使用 screen 混合模式的感觉：final = 1 - (1-base)*(1-blend)
                // 这里简单用加法，因为背景很黑
                finalColor += nebulaColor * totalNebula;
                
                // 稍微调整 gamma / 对比度
                finalColor = pow(finalColor, vec3(1.2)); 

                gl_FragColor = vec4(finalColor, 1.0);
            }
        `
    });
}

