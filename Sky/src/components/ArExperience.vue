<script setup lang="ts">
import { ref, onMounted } from 'vue';
import AFRAME from 'aframe';
import { zodiacData, type Constellation } from '../data/zodiac';
import { getCartesianPosition } from '../utils/astronomy';
import { createConstellationShape } from '../utils/constellationShapes';
import ZodiacInfo from './ZodiacInfo.vue';

// Use AFRAME's THREE to ensure compatibility
const THREE = (AFRAME as any).THREE;

// --- 1. ATMOSPHERIC SKY SHADER (Star Walk Style) ---
// Deep, realistic night sky gradient with horizon fading
if (!AFRAME.components['atmospheric-sky']) {
  AFRAME.registerComponent('atmospheric-sky', {
    init: function() {
      const geometry = new THREE.SphereGeometry(1000, 64, 32);
      const material = new THREE.ShaderMaterial({
        side: THREE.BackSide,
        uniforms: {
          topColor: { value: new THREE.Color('#000510') }, // Deep Space
          bottomColor: { value: new THREE.Color('#0b1d35') }, // Horizon Haze
          exponent: { value: 0.6 }
        },
        vertexShader: `
          varying vec3 vWorldPosition;
          void main() {
            vec4 worldPosition = modelMatrix * vec4( position, 1.0 );
            vWorldPosition = worldPosition.xyz;
            gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
          }
        `,
        fragmentShader: `
          uniform vec3 topColor;
          uniform vec3 bottomColor;
          uniform float exponent;
          varying vec3 vWorldPosition;
          void main() {
            float h = normalize( vWorldPosition + vec3(0.0, 200.0, 0.0) ).y;
            gl_FragColor = vec4( mix( bottomColor, topColor, max( pow( max( h , 0.0), exponent ), 0.0 ) ), 1.0 );
          }
        `
      });
      this.el.setObject3D('mesh', new THREE.Mesh(geometry, material));
    }
  });
}

// --- 2. REALISTIC WATER SHADER ---
// Water that reflects the "sky" color and moves
if (!AFRAME.components['ocean-water']) {
  AFRAME.registerComponent('ocean-water', {
    init: function() {
      const geometry = new THREE.PlaneGeometry(2000, 2000, 64, 64);
      geometry.rotateX(-Math.PI / 2);
      
      const material = new THREE.ShaderMaterial({
        uniforms: {
          time: { value: 0 },
          color: { value: new THREE.Color('#051a30') }
        },
        vertexShader: `
          varying vec2 vUv;
          uniform float time;
          void main() {
            vUv = uv;
            vec3 pos = position;
            // Simple wave displacement
            pos.y += sin(pos.x * 0.05 + time) * 2.0;
            pos.y += cos(pos.z * 0.05 + time) * 2.0;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
          }
        `,
        fragmentShader: `
          varying vec2 vUv;
          uniform vec3 color;
          uniform float time;
          
          // Simple fake reflection/sparkle
          float random(vec2 st) {
              return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
          }

          void main() {
            // Water grid pattern
            float grid = step(0.98, sin(vUv.x * 200.0 + time) * sin(vUv.y * 200.0 + time));
            
            vec3 waterColor = color;
            
            // Add some "foam" or reflection at peaks
            waterColor += vec3(0.2) * grid;
            
            // Fade out into distance
            float dist = distance(vUv, vec2(0.5));
            float alpha = smoothstep(0.5, 0.0, dist);
            
            gl_FragColor = vec4(waterColor, 0.8 * alpha);
          }
        `,
        transparent: true,
        blending: THREE.NormalBlending
      });

      this.el.setObject3D('mesh', new THREE.Mesh(geometry, material));
      this.material = material;
    },
    tick: function(_t: number, dt: number) {
      if (this.material) this.material.uniforms.time.value += dt / 1000;
    }
  });
}

// --- 3. MILKY WAY BAND (Realistic) ---
// A static, beautiful texture-based or procedural band
if (!AFRAME.components['milky-way']) {
  AFRAME.registerComponent('milky-way', {
    init: function() {
      // We use a curved plane (part of a cylinder or sphere)
      const geometry = new THREE.CylinderGeometry(600, 600, 300, 64, 1, true, 0, Math.PI);
      geometry.rotateZ(Math.PI / 3); // Tilt it
      geometry.scale(1, 0.5, 1); // Flatten slightly
      
      const vertexShader = `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `;

      const fragmentShader = `
        varying vec2 vUv;
        
        // Cloud noise function
        float hash( float n ) { return fract(sin(n)*43758.5453123); }
        float noise( in vec3 x ) {
            vec3 p = floor(x);
            vec3 f = fract(x);
            f = f*f*(3.0-2.0*f);
            float n = p.x + p.y*57.0 + p.z*113.0;
            return mix(mix(mix( hash(n+  0.0), hash(n+  1.0),f.x),
                           mix( hash(n+ 57.0), hash(n+ 58.0),f.x),f.y),
                       mix(mix( hash(n+113.0), hash(n+114.0),f.x),
                           mix( hash(n+170.0), hash(n+171.0),f.x),f.y),f.z);
        }

        void main() {
          // Generate cloud pattern
          float n = noise(vec3(vUv.x * 10.0, vUv.y * 4.0, 0.0));
          n += 0.5 * noise(vec3(vUv.x * 20.0, vUv.y * 8.0, 1.0));
          
          // Mask edges to fade out
          float alpha = smoothstep(0.0, 0.5, vUv.y) * smoothstep(1.0, 0.5, vUv.y);
          alpha *= smoothstep(0.0, 0.2, vUv.x) * smoothstep(1.0, 0.8, vUv.x);
          
          // Purple/Blue/Pink gradient
          vec3 color = mix(vec3(0.1, 0.0, 0.2), vec3(0.4, 0.2, 0.6), n);
          color = mix(color, vec3(0.8, 0.6, 0.4), pow(n, 3.0)); // Add some golden dust centers
          
          gl_FragColor = vec4(color, alpha * 0.4); // Semi-transparent
        }
      `;

      const material = new THREE.ShaderMaterial({
        side: THREE.DoubleSide,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        vertexShader,
        fragmentShader
      });

      this.el.setObject3D('mesh', new THREE.Mesh(geometry, material));
    }
  });
}

// --- 4. METEOR SHOWER (Shooting Stars) ---
if (!AFRAME.components['meteor-shower']) {
  AFRAME.registerComponent('meteor-shower', {
    init: function() {
      this.meteors = [];
      this.geometry = new THREE.BufferGeometry();
      // Max 10 active meteors
      const positions = new Float32Array(10 * 2 * 3); // Start and End points
      this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      
      const material = new THREE.LineBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.8
      });
      
      this.mesh = new THREE.LineSegments(this.geometry, material);
      this.el.setObject3D('mesh', this.mesh);
      
      this.lastMeteorTime = 0;
    },
    tick: function(t: number, dt: number) {
      // Spawn meteor every 2-5 seconds
      if (t - this.lastMeteorTime > 2000 + Math.random() * 3000) {
        this.spawnMeteor();
        this.lastMeteorTime = t;
      }
      this.updateMeteors(dt);
    },
    spawnMeteor: function() {
      // Random point on sphere
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = 400;
      
      const start = new THREE.Vector3(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.cos(phi),
        r * Math.sin(phi) * Math.sin(theta)
      );
      
      // Velocity tangent to sphere roughly
      const velocity = new THREE.Vector3(
        Math.random()-0.5, Math.random()-0.5, Math.random()-0.5
      ).normalize().multiplyScalar(0.8); // speed
      
      this.meteors.push({ start, velocity, age: 0, life: 1000 }); // 1s life
    },
    updateMeteors: function(dt: number) {
      const positions = this.mesh.geometry.attributes.position.array;
      let activeCount = 0;
      
      // Loop backwards to allow removal
      for (let i = this.meteors.length - 1; i >= 0; i--) {
        const m = this.meteors[i];
        m.age += dt;
        
        if (m.age > m.life) {
          this.meteors.splice(i, 1);
          continue;
        }
        
        // Update head position
        const currentPos = m.start.clone().add(m.velocity.clone().multiplyScalar(m.age));
        // Tail is slightly behind
        const tailPos = currentPos.clone().sub(m.velocity.clone().multiplyScalar(200)); 
        
        // Update buffer
        positions[activeCount * 6 + 0] = tailPos.x;
        positions[activeCount * 6 + 1] = tailPos.y;
        positions[activeCount * 6 + 2] = tailPos.z;
        
        positions[activeCount * 6 + 3] = currentPos.x;
        positions[activeCount * 6 + 4] = currentPos.y;
        positions[activeCount * 6 + 5] = currentPos.z;
        
        activeCount++;
      }
      
      // Clear remaining buffer
      for (let i = activeCount * 6; i < positions.length; i++) {
        positions[i] = 0;
      }
      
      this.mesh.geometry.attributes.position.needsUpdate = true;
      this.mesh.geometry.setDrawRange(0, activeCount * 2);
    }
  });
}

// --- ZODIAC STAR (Interactive Clickable Stars) ---
if (!AFRAME.components['zodiac-star']) {
  AFRAME.registerComponent('zodiac-star', {
    schema: { 
      id: { type: 'string' }, 
      color: { type: 'string', default: '#FFF' } 
    },
    init: function() {
      // Add click event
      this.el.addEventListener('click', () => {
        console.log('Star clicked:', this.data.id); // Debug log
        this.el.sceneEl.emit('zodiac-click', { id: this.data.id });
      });
      
      // Add hover effect
      this.el.addEventListener('mouseenter', () => {
        this.el.setAttribute('scale', { x: 1.5, y: 1.5, z: 1.5 });
      });
      
      this.el.addEventListener('mouseleave', () => {
        this.el.setAttribute('scale', { x: 1, y: 1, z: 1 });
      });
    }
  });
}

// --- ZODIAC 3D SHAPES (Real Animal Forms with Particle Effects) ---
if (!AFRAME.components['constellation-art']) {
    AFRAME.registerComponent('constellation-art', {
        schema: { id: {type:'string'} },
        init: function() {
            console.log('Creating 3D shape for:', this.data.id);
            
            const mainGroup = new THREE.Group();
            
            // 1. Create the 3D shape
            const shape = createConstellationShape(this.data.id, THREE);
            if (!shape) {
                console.error('Failed to create shape for:', this.data.id);
                return;
            }
            shape.scale.set(1.5, 1.5, 1.5);
            mainGroup.add(shape);
            
            // 2. Add flowing particle stream around the shape
            const particleCount = 300;
            const particleGeo = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const velocities = [];
            
            for (let i = 0; i < particleCount; i++) {
                // Spiral distribution
                const angle = (i / particleCount) * Math.PI * 8;
                const radius = 15 + (i / particleCount) * 20;
                const height = (i / particleCount) * 40 - 20;
                
                positions[i * 3] = Math.cos(angle) * radius;
                positions[i * 3 + 1] = height;
                positions[i * 3 + 2] = Math.sin(angle) * radius;
                
                velocities.push({
                    angle: angle,
                    radius: radius,
                    speed: 0.01 + Math.random() * 0.02
                });
            }
            
            particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            
            const particleMat = new THREE.PointsMaterial({
                color: 0xaaddff,
                size: 1.2,
                transparent: true,
                opacity: 0.8,
                blending: THREE.AdditiveBlending
            });
            
            const particles = new THREE.Points(particleGeo, particleMat);
            mainGroup.add(particles);
            
            this.el.setObject3D('mesh', mainGroup);
            this.shape = shape;
            this.particles = particles;
            this.velocities = velocities;
            this.time = 0;
            
            console.log('Shape created successfully for:', this.data.id);
        },
        tick: function(_t: any, dt: any) {
            this.time = (this.time || 0) + dt * 0.001;
            
            // Rotate the main shape
            if (this.shape) {
                this.shape.rotation.y += 0.0008 * dt;
                
                // Enhanced breathing effect
                const breathe = 1 + Math.sin(this.time * 2) * 0.12;
                this.shape.scale.set(1.5 * breathe, 1.5 * breathe, 1.5 * breathe);
            }
            
            // Animate flowing particles in spiral
            if (this.particles && this.velocities) {
                const positions = this.particles.geometry.attributes.position.array;
                
                for (let i = 0; i < this.velocities.length; i++) {
                    const vel = this.velocities[i];
                    vel.angle += vel.speed;
                    
                    // Update position in spiral
                    positions[i * 3] = Math.cos(vel.angle) * vel.radius;
                    positions[i * 3 + 2] = Math.sin(vel.angle) * vel.radius;
                    
                    // Slight vertical oscillation
                    positions[i * 3 + 1] += Math.sin(this.time * 3 + i * 0.1) * 0.1;
                }
                
                this.particles.geometry.attributes.position.needsUpdate = true;
                
                // Pulse particle brightness
                const pulseBrightness = 0.6 + Math.sin(this.time * 2) * 0.4;
                this.particles.material.opacity = pulseBrightness;
            }
        }
    });
}

// --- VUE LOGIC ---
const isArMode = ref(false);
const selectedConstellation = ref<Constellation | null>(null);
const infoVisible = ref(false);

const toggleAr = () => isArMode.value = !isArMode.value;
const closeInfo = () => infoVisible.value = false;

const onZodiacClick = (e: CustomEvent) => {
  const id = e.detail.id;
  const data = zodiacData.find(c => c.id === id);
  if (data) {
    selectedConstellation.value = data;
    infoVisible.value = true;
  }
};

// Calculate center of constellation for "Art" placement
const getCenter = (c: Constellation) => {
    let x=0, y=0, z=0;
    c.stars.forEach(s => {
        const p = getCartesianPosition(s.ra, s.dec, 450);
        x+=p.x; y+=p.y; z+=p.z;
    });
    const len = c.stars.length;
    return `${x/len} ${y/len} ${z/len}`;
};

// Line logic (Enhanced brightness and color-coding)
const getLineCoords = (c: Constellation, indices: number[]) => {
    if (indices.length < 2 || indices[0] === undefined || indices[1] === undefined) return '';
    const idx1 = indices[0];
    const idx2 = indices[1];
    if(!c.stars[idx1] || !c.stars[idx2]) return '';
    const p1 = getCartesianPosition(c.stars[idx1].ra, c.stars[idx1].dec, 450);
    const p2 = getCartesianPosition(c.stars[idx2].ra, c.stars[idx2].dec, 450);
    
    // Brighter, element-coded colors
    const lineColor = c.element === 'Fire' ? '#ffcc88' : 
                      c.element === 'Water' ? '#88ccff' : 
                      c.element === 'Earth' ? '#aabb88' : 
                      '#ccddff'; // Air
    
    return `start: ${p1.x} ${p1.y} ${p1.z}; end: ${p2.x} ${p2.y} ${p2.z}; color: ${lineColor}; opacity: 0.8`;
}

onMounted(() => {
  const scene = document.querySelector('a-scene');
  if (scene) scene.addEventListener('zodiac-click', onZodiacClick as EventListener);
  
  // Procedural glow asset
  const canvas = document.createElement('canvas');
  canvas.width = 64; canvas.height = 64;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    const grad = ctx.createRadialGradient(32,32,0, 32,32,32);
    grad.addColorStop(0, 'rgba(255,255,255,1)');
    grad.addColorStop(0.2, 'rgba(200,220,255,0.5)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0,0,64,64);
    document.getElementById('glow-texture')?.setAttribute('src', canvas.toDataURL());
  }
});
</script>

<template>
  <div class="wrapper">
    <!-- HUD -->
    <div class="hud">
      <div class="top-bar">
        <div class="logo">STAR <span class="thin">WALK</span> AR</div>
        <div class="compass">N</div>
      </div>
      <div class="bottom-bar">
        <button class="ar-toggle" @click="toggleAr">
          <span v-if="!isArMode">👁️ View AR</span>
          <span v-else>🌌 View Sky</span>
        </button>
      </div>
    </div>

    <ZodiacInfo :data="selectedConstellation" :visible="infoVisible" @close="closeInfo" />

    <a-scene 
      embedded 
      renderer="antialias: true; colorManagement: true; physicallyCorrectLights: true;" 
      vr-mode-ui="enabled: false"
      raycaster="objects: .clickable"
      cursor="rayOrigin: mouse"
    >
      <a-assets>
        <img id="glow-texture" src="" />
      </a-assets>

      <a-camera position="0 0 0" look-controls="magicWindowTrackingEnabled: true; reverseMouseDrag: true"></a-camera>

      <!-- Environment -->
      <a-entity v-if="!isArMode">
          <!-- 1. Atmospheric Sky -->
          <a-entity atmospheric-sky></a-entity>
          <!-- 2. Water Reflection -->
          <a-entity ocean-water position="0 -100 0"></a-entity>
          <!-- 3. Milky Way Band -->
          <a-entity milky-way position="0 200 0"></a-entity>
      </a-entity>

      <!-- Dynamic Elements -->
      <a-entity meteor-shower></a-entity>
      
      <!-- Star Field (Background stars) -->
      <a-entity star-field="count: 8000"></a-entity>

      <!-- Constellations -->
      <a-entity id="zodiac-container">
        <a-entity v-for="c in zodiacData" :key="c.id">
            
            <!-- 3D Constellation Shape (Center of Constellation) -->
            <a-entity 
                v-if="!isArMode"
                :constellation-art="`id: ${c.id}`"
                :position="getCenter(c)"
            ></a-entity>

            <!-- Stars (Enhanced Brightness) -->
            <a-entity v-for="(s, i) in c.stars" :key="i" :position="getCartesianPosition(s.ra, s.dec, 450)">
                <!-- Main Star Glow (Bigger & Brighter) -->
                <a-image 
                    src="#glow-texture" 
                    :scale="`${3 + (5 - s.mag) * 1.5} ${3 + (5 - s.mag) * 1.5} 1`"
                    look-at="[camera]"
                    :color="s.color"
                    opacity="0.95"
                    material="blending: additive"
                    class="clickable"
                    :zodiac-star="`id: ${c.id}; color: ${s.color}`"
                ></a-image>
            </a-entity>

            <!-- Connecting Lines -->
            <a-entity v-for="(line, k) in c.lines" :key="`l-${k}`"
                :line="getLineCoords(c, line)"
            ></a-entity>

            <!-- Label (Brighter & With Glow) -->
            <a-entity 
                v-if="c.stars[0]"
                :position="getCartesianPosition(c.stars[0].ra, c.stars[0].dec, 450)" 
                look-at="[camera]"
            >
                <a-text 
                    :value="c.name" 
                    align="center" 
                    position="0 -4 0" 
                    color="#ffffff" 
                    opacity="0.95" 
                    width="18"
                    shader="msdf"
                    negate="false"
                ></a-text>
            </a-entity>

        </a-entity>
      </a-entity>

      <!-- Enhanced Lighting for Better Visibility -->
      <a-light type="ambient" color="#556677" intensity="1.2"></a-light>
      <a-light type="point" position="0 50 0" intensity="2.0" color="#ffffff" distance="2000"></a-light>
      <a-light type="point" position="100 -50 100" intensity="1.0" color="#88ccff"></a-light>

    </a-scene>
  </div>
</template>

<style scoped>
.wrapper {
  width: 100vw; height: 100vh;
  background: black;
  overflow: hidden;
  font-family: 'Helvetica Neue', sans-serif;
}
a-scene { width: 100%; height: 100%; }

.hud {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 10;
  display: flex; flex-direction: column; justify-content: space-between; padding: 2rem;
}

.top-bar { display: flex; justify-content: space-between; align-items: center; }
.logo { color: white; font-size: 1.5rem; font-weight: 700; letter-spacing: 2px; text-shadow: 0 0 10px rgba(0,100,255,0.8); }
.logo .thin { font-weight: 300; opacity: 0.8; }
.compass { color: #aaddff; border: 2px solid #aaddff; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; background: rgba(0,20,40,0.5); backdrop-filter: blur(5px); }

.bottom-bar { display: flex; justify-content: center; pointer-events: auto; }
.ar-toggle {
  background: linear-gradient(135deg, rgba(0,50,100,0.6), rgba(0,20,40,0.8));
  border: 1px solid rgba(100,200,255,0.3);
  color: #fff;
  padding: 15px 40px;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(0,100,255,0.3);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}
.ar-toggle:hover {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(0,100,255,0.6);
  border-color: #fff;
}
</style>
