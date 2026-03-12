import * as THREE from 'three'
import type { StarMeta } from '../../../../../gen/ts/models/StarMeta'
import type { GPS } from '../../../../../gen/ts/models/GPS'
import { loadStarCatalog } from '../astronomy/star-catalog'
import { getStarName } from '../data/star-names'
import { absoluteOrientationManager, AbsoluteOrientationData } from '../sensors/AbsoluteOrientation'
import { raDecToVector3 } from '../astronomy/cartesian-coordinate'
import { convertHorizontalQuaternionToEquatorialQuaternionPro } from '../astronomy/astronomy'

const STELLARIUM_BV_START = -0.335
const STELLARIUM_BV_FINISH = 3.347
const STELLARIUM_BV_COLORS: ReadonlyArray<readonly [number, number, number]> = [
  [0.602745, 0.713725, 1.0],
  [0.604902, 0.715294, 1.0],
  [0.607059, 0.716863, 1.0],
  [0.609215, 0.718431, 1.0],
  [0.611372, 0.72, 1.0],
  [0.613529, 0.721569, 1.0],
  [0.63549, 0.737255, 1.0],
  [0.651059, 0.749673, 1.0],
  [0.666627, 0.762092, 1.0],
  [0.682196, 0.77451, 1.0],
  [0.697764, 0.786929, 1.0],
  [0.713333, 0.799347, 1.0],
  [0.730306, 0.811242, 1.0],
  [0.747278, 0.823138, 1.0],
  [0.764251, 0.835033, 1.0],
  [0.781223, 0.846929, 1.0],
  [0.798196, 0.858824, 1.0],
  [0.812282, 0.868236, 1.0],
  [0.826368, 0.877647, 1.0],
  [0.840455, 0.887059, 1.0],
  [0.854541, 0.89647, 1.0],
  [0.868627, 0.905882, 1.0],
  [0.884627, 0.916862, 1.0],
  [0.900627, 0.927843, 1.0],
  [0.916627, 0.938823, 1.0],
  [0.932627, 0.949804, 1.0],
  [0.948627, 0.960784, 1.0],
  [0.964444, 0.972549, 1.0],
  [0.980261, 0.984313, 1.0],
  [0.996078, 0.996078, 1.0],
  [1.0, 1.0, 1.0],
  [1.0, 0.999643, 0.999287],
  [1.0, 0.999287, 0.998574],
  [1.0, 0.99893, 0.997861],
  [1.0, 0.998574, 0.997148],
  [1.0, 0.998217, 0.996435],
  [1.0, 0.997861, 0.995722],
  [1.0, 0.997504, 0.995009],
  [1.0, 0.997148, 0.994296],
  [1.0, 0.996791, 0.993583],
  [1.0, 0.996435, 0.99287],
  [1.0, 0.996078, 0.992157],
  [1.0, 0.99114, 0.981554],
  [1.0, 0.986201, 0.970951],
  [1.0, 0.981263, 0.960349],
  [1.0, 0.976325, 0.949746],
  [1.0, 0.971387, 0.939143],
  [1.0, 0.966448, 0.92854],
  [1.0, 0.96151, 0.917938],
  [1.0, 0.956572, 0.907335],
  [1.0, 0.951634, 0.896732],
  [1.0, 0.946695, 0.886129],
  [1.0, 0.941757, 0.875526],
  [1.0, 0.936819, 0.864924],
  [1.0, 0.931881, 0.854321],
  [1.0, 0.926942, 0.843718],
  [1.0, 0.922004, 0.833115],
  [1.0, 0.917066, 0.822513],
  [1.0, 0.912128, 0.81191],
  [1.0, 0.907189, 0.801307],
  [1.0, 0.902251, 0.790704],
  [1.0, 0.897313, 0.780101],
  [1.0, 0.892375, 0.769499],
  [1.0, 0.887436, 0.758896],
  [1.0, 0.882498, 0.748293],
  [1.0, 0.87756, 0.73769],
  [1.0, 0.872622, 0.727088],
  [1.0, 0.867683, 0.716485],
  [1.0, 0.862745, 0.705882],
  [1.0, 0.858617, 0.695975],
  [1.0, 0.85449, 0.686068],
  [1.0, 0.850362, 0.676161],
  [1.0, 0.846234, 0.666254],
  [1.0, 0.842107, 0.656346],
  [1.0, 0.837979, 0.646439],
  [1.0, 0.833851, 0.636532],
  [1.0, 0.829724, 0.626625],
  [1.0, 0.825596, 0.616718],
  [1.0, 0.821468, 0.606811],
  [1.0, 0.81734, 0.596904],
  [1.0, 0.813213, 0.586997],
  [1.0, 0.809085, 0.57709],
  [1.0, 0.804957, 0.567183],
  [1.0, 0.80083, 0.557275],
  [1.0, 0.796702, 0.547368],
  [1.0, 0.792574, 0.537461],
  [1.0, 0.788447, 0.527554],
  [1.0, 0.784319, 0.517647],
  [1.0, 0.784025, 0.520882],
  [1.0, 0.783731, 0.524118],
  [1.0, 0.783436, 0.527353],
  [1.0, 0.783142, 0.530588],
  [1.0, 0.782848, 0.533824],
  [1.0, 0.782554, 0.537059],
  [1.0, 0.782259, 0.540294],
  [1.0, 0.781965, 0.543529],
  [1.0, 0.781671, 0.546765],
  [1.0, 0.781377, 0.55],
  [1.0, 0.781082, 0.553235],
  [1.0, 0.780788, 0.556471],
  [1.0, 0.780494, 0.559706],
  [1.0, 0.7802, 0.562941],
  [1.0, 0.779905, 0.566177],
  [1.0, 0.779611, 0.569412],
  [1.0, 0.779317, 0.572647],
  [1.0, 0.779023, 0.575882],
  [1.0, 0.778728, 0.579118],
  [1.0, 0.778434, 0.582353],
  [1.0, 0.77814, 0.585588],
  [1.0, 0.777846, 0.588824],
  [1.0, 0.777551, 0.592059],
  [1.0, 0.777257, 0.595294],
  [1.0, 0.776963, 0.59853],
  [1.0, 0.776669, 0.601765],
  [1.0, 0.776374, 0.605],
  [1.0, 0.77608, 0.608235],
  [1.0, 0.775786, 0.611471],
  [1.0, 0.775492, 0.614706],
  [1.0, 0.775197, 0.617941],
  [1.0, 0.774903, 0.621177],
  [1.0, 0.774609, 0.624412],
  [1.0, 0.774315, 0.627647],
  [1.0, 0.77402, 0.630883],
  [1.0, 0.773726, 0.634118],
  [1.0, 0.773432, 0.637353],
  [1.0, 0.773138, 0.640588],
  [1.0, 0.772843, 0.643824],
  [1.0, 0.772549, 0.647059],
]

/**
 * Star click information
 */
export interface StarClickInfo {
  hip: number
  name: string
  englishName: string
  constellation: string
  magnitude: number
  bvColor: number
  distance?: number
  rightAscension: number
  declination: number
  altitude: number
  azimuth: number
  screenX: number
  screenY: number
  originalName: string
  description: string
  url: string
  raw?: any
}

export type StartrailRenderOptions = {
  shotIntervalSeconds: number
  startTimestampMs: number
  durationSeconds: number
  twinkleMultiplier: number
  renderStarSizeMultiplier: number
  renderStarBrightnessMultiplier: number
  frameIntervalSeconds?: number
}

/**
 * Ground Observer Renderer
 * Simulates sky view from Earth surface
 */
export class GroundObserverRenderer {
  // millisecond
  public timestamp: number = 1772069929000
  public location: GPS = { longitude: -6.2603, latitude: 53.3498 }
  public renderStarSizeMultiplier: number = 1.0
  public renderStarBrightnessMultiplier: number = 1.0
  private maxStarRadius: number = 8.0
  private minStarRadius: number = 3.0
  private maxStarBrightness: number = 1.5
  private minStarBrightness: number = 0.1

  private scene: THREE.Scene
  // 用于AR渲染的camera，不是设备的camera
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private container: HTMLElement

  // Render objects
  private starPoints: THREE.Points | null = null
  private ground: THREE.Mesh | null = null
  private horizon: THREE.Line | null = null
  private constellationModels: THREE.Group = new THREE.Group()
  private constellationLines: THREE.Group = new THREE.Group()

  // Star data
  private starMap: Map<number, { star: StarMeta; position: THREE.Vector3 }> = new Map()
  private starCatalog: StarMeta[] = []

  // Celestial sphere
  private readonly SKY_RADIUS = 1000

  // Animation
  private animationFrameId: number | null = null
  private arCameraUpdateIntervalId: number | null = null
  private startrailFrameIntervalId: number | null = null
  private renderStartTimeMs: number = performance.now()
  private readonly defaultAutoClear = true
  private orientationUpdatesEnabled = true
  private renderMode: 'AR' | 'STARTRAIL' = 'AR'
  private startrailTwinkleMultiplier = 1
  private pendingStartrailResolve: (() => void) | null = null
  private absoluteOrientationListener: ((quaternion: AbsoluteOrientationData) => void) | null = null

  // AR mode
  private arMode: boolean = false

  private absoluteOrientation: [number, number, number, number] = [0, 0, 0, 1] // 四元数数据

  // Camera
  private videoElement: HTMLVideoElement | null = null
  private videoStream: MediaStream | null = null

  // Click detection
  private raycaster: THREE.Raycaster = new THREE.Raycaster()
  private mouse: THREE.Vector2 = new THREE.Vector2()
  private onStarClickCallback: ((starInfo: StarClickInfo) => void) | null = null
  private selectedStarIndicator: THREE.Sprite | null = null

  constructor(container: HTMLElement) {
    this.container = container

    this.scene = new THREE.Scene()
    this.scene.background = null

    // FOV tuned for mobile camera matching
    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      this.SKY_RADIUS * 2,
    )

    this.camera.position.set(0, 0, 0)
    this.camera.lookAt(0, 1, 0)
    this.camera.up.set(0, 1, 0)

    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true,
    })
    this.renderer.autoClear = this.defaultAutoClear
    this.renderer.setSize(window.innerWidth, window.innerHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.0
    container.appendChild(this.renderer.domElement)

    // this.createGround();
    // this.createHorizon();
    this.setupLighting()

    this.loadStarField()
    this.startARRenderLoop()
    this.setupClickDetection()

    window.addEventListener('resize', this.onWindowResize)
    window.addEventListener('orientationchange', () => {
      setTimeout(this.onWindowResize, 200)
    })

    this.absoluteOrientationListener = (quaternion: AbsoluteOrientationData) => {
      if (!this.orientationUpdatesEnabled) return
      const q = quaternion.quaternion
      this.absoluteOrientation = [q.x, q.y, q.z, q.w]
      this.updateARCameraLookAt()
    }
    absoluteOrientationManager.addListener(this.absoluteOrientationListener)
    absoluteOrientationManager.startListening()

    // Fallback update loop for devices without sensor updates
    this.arCameraUpdateIntervalId = window.setInterval(() => {
      if (!this.orientationUpdatesEnabled) return
      this.updateARCameraLookAt()
    }, 100)

    console.log('Ground Observer Renderer initialized')
  }

  // 更新AR渲染时的lookat
  private updateARCameraLookAt() {
    const [x, y, z, w] = this.absoluteOrientation
    // Convert horizontal quaternion to equatorial quaternion for camera
    let ans = convertHorizontalQuaternionToEquatorialQuaternionPro(
      [x, y, z, w],
      this.timestamp,
      this.location,
    )
    this.camera.quaternion.set(ans[0], ans[1], ans[2], ans[3])
  }

  private setupLighting(): void {
    const ambientLight = new THREE.AmbientLight(0x202040, 0.2)
    this.scene.add(ambientLight)
  }

  private async loadStarField(): Promise<void> {
    try {
      console.log('Loading star catalog...')
      const stars = await loadStarCatalog()
      this.starCatalog = stars
      this.createStarFieldFromCatalog(stars)
      console.log('star catalog loaded')
    } catch (error) {
      console.error('Failed to load star catalog:', error)
    }
  }

  private createStarFieldFromCatalog(stars: StarMeta[]): void {
    const brightStars: {
      pos: THREE.Vector3
      color: THREE.Color
      star: StarMeta
      size: number
      brightness: number
    }[] = []
    const mediumStars: {
      pos: THREE.Vector3
      color: THREE.Color
      star: StarMeta
      size: number
      brightness: number
    }[] = []

    this.starMap.clear()

    stars.forEach((star) => {
      const pos = raDecToVector3(
        star.equatorialCoordinate.rightAscension,
        star.equatorialCoordinate.declination,
        this.SKY_RADIUS,
      )
      const color = this.bvToRGB(star.bvColor)
      const size = this.getStarSize(star.magnitude)
      const brightness = this.getStarBrightness(star.magnitude)
      this.starMap.set(star.hIP, { star, position: pos })

      const starData = { pos, color, star, size, brightness }
      if (star.magnitude < 1.0) brightStars.push(starData)
      else mediumStars.push(starData)
    })

    if (this.starPoints) this.scene.remove(this.starPoints)

    const starGroup = new THREE.Group()
    starGroup.name = 'Stars'

    if (brightStars.length > 0)
      starGroup.add(this.createStarPoints(brightStars, '/texture/star16x16_ray.png'))
    if (mediumStars.length > 0)
      starGroup.add(this.createStarPoints(mediumStars, '/texture/star16x16.png'))

    this.starPoints = starGroup as any
    this.scene.add(starGroup)
  }

  private getStarSize(magnitude: number): number {
    if (magnitude <= 1) {
      return this.renderStarSizeMultiplier * this.maxStarRadius
    }
    if (magnitude >= 6) {
      return this.renderStarSizeMultiplier * this.minStarRadius
    }
    return (
      this.renderStarSizeMultiplier *
      (this.maxStarRadius - ((magnitude - 1) / 5) * (this.maxStarRadius - this.minStarRadius))
    )
  }

  private getStarBrightness(magnitude: number): number {
    if (magnitude <= 1) {
      return this.renderStarBrightnessMultiplier * this.maxStarBrightness
    }
    if (magnitude >= 6) {
      return this.renderStarBrightnessMultiplier * this.minStarBrightness
    }
    return (
      this.renderStarBrightnessMultiplier *
      (this.maxStarBrightness -
        ((magnitude - 1) / 5) * (this.maxStarBrightness - this.minStarBrightness))
    )
  }

  private createStarPoints(
    starsData: {
      pos: THREE.Vector3
      color: THREE.Color
      star: StarMeta
      size: number
      brightness: number
    }[],
    texturePath: string,
  ): THREE.Points {
    const positions: number[] = []
    const colors: number[] = []
    const magnitudes: number[] = []
    const twinklePhases: number[] = []
    const hips: number[] = []
    const sizes: number[] = []
    const brightnesses: number[] = []

    starsData.forEach(({ pos, color, star, size, brightness }) => {
      positions.push(pos.x, pos.y, pos.z)
      colors.push(color.r, color.g, color.b)
      magnitudes.push(star.magnitude)
      twinklePhases.push(Math.random() * Math.PI * 2)
      hips.push(star.hIP)
      sizes.push(size)
      brightnesses.push(brightness)
    })

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
    geometry.setAttribute('magnitude', new THREE.Float32BufferAttribute(magnitudes, 1))
    geometry.setAttribute('twinklePhase', new THREE.Float32BufferAttribute(twinklePhases, 1))
    geometry.setAttribute('hip', new THREE.Float32BufferAttribute(hips, 1))
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))
    geometry.setAttribute('brightness', new THREE.Float32BufferAttribute(brightnesses, 1))

    const isRayTexture = texturePath.includes('ray')
    const texture = this.createProceduralStarTexture(isRayTexture)
    const material = this.createTwinkleStarMaterial(texture)

    return new THREE.Points(geometry, material)
  }

  private createTwinkleStarMaterial(texture: THREE.Texture): THREE.ShaderMaterial {
    return new THREE.RawShaderMaterial({
      uniforms: {
        uTexture: { value: texture },
        uTime: { value: 0 },
        uPixelRatio: { value: window.devicePixelRatio },
        uIsStartrailMode: { value: 0 },
        uTwinkleMultiplier: { value: 1 },
      },
      vertexShader: `
                precision mediump float;
                precision mediump int;
                uniform mat4 modelViewMatrix;
                uniform mat4 projectionMatrix;
                attribute vec3 position;
                attribute vec3 color;
                attribute float magnitude;
                attribute float twinklePhase;
                attribute float size;
                attribute float brightness;
                uniform float uTime;
                uniform float uPixelRatio;
                uniform float uIsStartrailMode;
                uniform float uTwinkleMultiplier;
                varying vec3 vColor;
                varying float vTwinkle;
                varying float vBrightness;
                float rand01(vec2 p) {
                  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
                }
                void main() {
                    vColor = color;
                    vBrightness = brightness;
                    float twinkleSpeed = 1.0 + magnitude * 0.3;
                  if (uIsStartrailMode > 0.5) {
                    float twinkleRandom = rand01(vec2(twinklePhase + magnitude, uTime * twinkleSpeed)) * 2.0 - 1.0;
                    vTwinkle = 1.0 + uTwinkleMultiplier * twinkleRandom;
                  } else {
                    float twinkle = sin(uTime * twinkleSpeed + twinklePhase);
                    vTwinkle = 1.0 + 0.2 * twinkle;
                  }
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = size * vTwinkle * uPixelRatio;
                }
            `,
      fragmentShader: `
              precision mediump float;
              precision mediump int;
                uniform sampler2D uTexture;
                varying vec3 vColor;
                varying float vTwinkle;
                varying float vBrightness;
                void main() {
                    vec4 texColor = texture2D(uTexture, gl_PointCoord);
                    vec3 finalColor = texColor.rgb * vColor * vTwinkle * vBrightness;
                    float alpha = texColor.a * vBrightness;
                    gl_FragColor = vec4(finalColor, alpha);
                }
            `,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
  }

  private createProceduralStarTexture(withRays: boolean = false): THREE.CanvasTexture {
    const size = 128
    const canvas = document.createElement('canvas')
    canvas.width = size
    canvas.height = size
    const ctx = canvas.getContext('2d')!
    ctx.clearRect(0, 0, size, size)
    const center = size / 2

    if (withRays) {
      ctx.save()
      ctx.translate(center, center)
      const rayLength = size * 0.45
      const rayWidth = 2
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
      ctx.lineWidth = rayWidth
      ctx.lineCap = 'round'
      for (let i = 0; i < 4; i++) {
        ctx.rotate(Math.PI / 4)
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(0, -rayLength)
        ctx.stroke()
        ctx.rotate(Math.PI / 4)
      }
      ctx.restore()
    }

    const gradient = ctx.createRadialGradient(center, center, 0, center, center, size / 2)
    gradient.addColorStop(0, 'rgba(255,255,255,1.0)')
    gradient.addColorStop(0.3, 'rgba(255,255,255,0.8)')
    gradient.addColorStop(0.8, 'rgba(255,255,255,0.1)')
    gradient.addColorStop(1.0, 'rgba(255,255,255,0.0)')

    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, size, size)

    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    return texture
  }

  private bvToRGB(bv: number | null | undefined): THREE.Color {
    if (bv === null || bv === undefined || Number.isNaN(bv)) {
      return new THREE.Color(0, 0, 0)
    }

    const numColors = STELLARIUM_BV_COLORS.length

    if (bv <= STELLARIUM_BV_START) {
      const [r, g, b] = STELLARIUM_BV_COLORS[0]
      return new THREE.Color(r, g, b)
    }

    if (bv >= STELLARIUM_BV_FINISH) {
      const [r, g, b] = STELLARIUM_BV_COLORS[numColors - 1]
      return new THREE.Color(r, g, b)
    }

    const targetIndex = Math.floor(
      ((bv - STELLARIUM_BV_START) / (STELLARIUM_BV_FINISH - STELLARIUM_BV_START)) * numColors,
    )
    const [r, g, b] = STELLARIUM_BV_COLORS[targetIndex]
    return new THREE.Color(r, g, b)
  }

  public async enableARMode(): Promise<boolean> {
    console.log('Enabling AR mode...')
    if (typeof DeviceOrientationEvent === 'undefined') {
      console.error('Device orientation not supported')
      return false
    }

    this.arMode = true
    this.scene.background = null
    if (this.ground) this.ground.visible = false
    if (this.horizon) this.horizon.visible = false

    await this.startVideoStream()
    console.log('AR mode enabled')
    return true
  }

  public disableARMode(): void {
    if (!this.arMode) return

    this.arMode = false
    this.stopCamera()

    this.scene.background = null
    if (this.ground) this.ground.visible = true
    if (this.horizon) this.horizon.visible = true
    console.log('AR mode disabled')
  }

  /**
   * Main render loop with adaptive AR smoothing
   */
  private renderCurrentFrame = () => {
    const time = (performance.now() - this.renderStartTimeMs) * 0.001 // second
    const isStartrailMode = this.renderMode === 'STARTRAIL' ? 1 : 0
    const twinkleMultiplier = this.renderMode === 'STARTRAIL' ? this.startrailTwinkleMultiplier : 1

    if (this.starPoints) {
      this.starPoints.traverse((child: any) => {
        if (child instanceof THREE.Points && child.material instanceof THREE.ShaderMaterial) {
          child.material.uniforms.uTime.value = time
          child.material.uniforms.uIsStartrailMode.value = isStartrailMode
          child.material.uniforms.uTwinkleMultiplier.value = twinkleMultiplier
        }
      })
    }

    this.renderer.render(this.scene, this.camera)
  }

  private animate = () => {
    if (this.renderMode !== 'AR') {
      this.animationFrameId = null
      return
    }

    this.renderCurrentFrame()
    this.animationFrameId = requestAnimationFrame(this.animate)
  }

  private startARRenderLoop(): void {
    if (this.animationFrameId !== null) return
    this.animationFrameId = requestAnimationFrame(this.animate)
  }

  private stopARRenderLoop(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId)
      this.animationFrameId = null
    }
  }

  private clearStartrailLoop(): void {
    if (this.startrailFrameIntervalId !== null) {
      window.clearInterval(this.startrailFrameIntervalId)
      this.startrailFrameIntervalId = null
    }
  }

  public async generateStartrail(options: StartrailRenderOptions): Promise<void> {
    if (this.renderMode === 'STARTRAIL') {
      this.exitStartrailMode()
    }

    return new Promise<void>((resolve) => {
      this.pendingStartrailResolve = resolve
      this.enterStartrailMode(options)
    })
  }

  private enterStartrailMode(options: StartrailRenderOptions): void {
    const frameIntervalMs = 100
    const shotIntervalMs = Math.max(1, Math.round(options.shotIntervalSeconds * 1000))
    const totalDurationMs = Math.max(0, Math.round(options.durationSeconds * 1000))
    const totalFrames = Math.floor(totalDurationMs / shotIntervalMs)

    this.stopARRenderLoop()
    this.clearStartrailLoop()

    this.renderMode = 'STARTRAIL'
    this.orientationUpdatesEnabled = false
    this.renderer.autoClear = false
    this.clearSelectedStarIndicator()
    this.startrailTwinkleMultiplier = Math.max(0, options.twinkleMultiplier)
    this.renderStarSizeMultiplier = Math.max(0.01, options.renderStarSizeMultiplier)
    this.renderStarBrightnessMultiplier = Math.max(0.01, options.renderStarBrightnessMultiplier)

    if (this.starCatalog.length > 0) {
      this.createStarFieldFromCatalog(this.starCatalog)
    }

    this.timestamp = options.startTimestampMs
    this.updateARCameraLookAt()

    this.renderer.clear()

    if (totalFrames <= 0) {
      this.finishStartrailMode()
      return
    }

    let renderedFrames = 0
    this.startrailFrameIntervalId = window.setInterval(() => {
      if (renderedFrames >= totalFrames) {
        this.finishStartrailMode()
        return
      }

      this.timestamp += shotIntervalMs
      const currentFrame = renderedFrames + 1
      console.log(
        `[Startrail] frame ${currentFrame}/${totalFrames}, currentTimeMs=${this.timestamp}, currentTime=${new Date(this.timestamp).toISOString()}`,
      )
      this.updateARCameraLookAt()
      this.renderCurrentFrame()
      renderedFrames += 1

      if (renderedFrames >= totalFrames) {
        this.finishStartrailMode()
      }
    }, frameIntervalMs)
  }

  private finishStartrailMode(): void {
    this.clearStartrailLoop()

    if (this.pendingStartrailResolve) {
      this.pendingStartrailResolve()
      this.pendingStartrailResolve = null
    }
  }

  public exitStartrailMode(): void {
    if (this.renderMode !== 'STARTRAIL') return

    this.clearStartrailLoop()
    this.renderMode = 'AR'
    this.orientationUpdatesEnabled = true
    this.startrailTwinkleMultiplier = 1
    this.renderer.autoClear = this.defaultAutoClear
    this.renderer.clear()
    this.updateARCameraLookAt()
    this.startARRenderLoop()

    if (this.pendingStartrailResolve) {
      this.pendingStartrailResolve()
      this.pendingStartrailResolve = null
    }
  }

  public isARMode(): boolean {
    return this.arMode
  }

  private onWindowResize = () => {
    const width = window.innerWidth
    const height = window.innerHeight
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  }

  public dispose(): void {
    this.stopARRenderLoop()
    this.clearStartrailLoop()
    if (this.arCameraUpdateIntervalId !== null) {
      window.clearInterval(this.arCameraUpdateIntervalId)
      this.arCameraUpdateIntervalId = null
    }
    if (this.arMode) this.disableARMode()
    window.removeEventListener('resize', this.onWindowResize)

    this.clearSelectedStarIndicator()

    if (this.starPoints) {
      this.starPoints.geometry.dispose()
      if (this.starPoints.material instanceof THREE.Material) this.starPoints.material.dispose()
    }

    this.renderer.dispose()
    this.container.removeChild(this.renderer.domElement)
  }

  public setConstellationLinesVisible(visible: boolean): void {
    this.constellationLines.visible = visible
  }

  public setOnStarClick(callback: (starInfo: StarClickInfo) => void): void {
    this.onStarClickCallback = callback
  }

  private setupClickDetection(): void {
    this.raycaster.params.Points = { threshold: 20.0 }
    const handleClick = (clientX: number, clientY: number) => {
      if (this.renderMode === 'STARTRAIL') return

      const rect = this.renderer.domElement.getBoundingClientRect()
      const x = clientX - rect.left
      const y = clientY - rect.top
      this.mouse.x = (x / rect.width) * 2 - 1
      this.mouse.y = -(y / rect.height) * 2 + 1
      this.raycaster.setFromCamera(this.mouse, this.camera)
      if (this.starPoints) {
        const intersects = this.raycaster.intersectObject(this.starPoints, true)
        console.log(`click detcted, intersects with ${intersects.length} stars`)
        if (intersects.length > 0) {
          const bestHit = intersects.reduce((best, current) => {
            const bestDistanceToRay = best.distanceToRay ?? Number.POSITIVE_INFINITY
            const currentDistanceToRay = current.distanceToRay ?? Number.POSITIVE_INFINITY

            if (currentDistanceToRay < bestDistanceToRay) return current
            if (currentDistanceToRay > bestDistanceToRay) return best
            return current.distance < best.distance ? current : best
          })

          if (bestHit.index !== undefined) {
            const hitObject = bestHit.object as THREE.Points
            const hipAttribute = hitObject.geometry.getAttribute('hip') as
              | THREE.BufferAttribute
              | THREE.InterleavedBufferAttribute
              | undefined

            if (hipAttribute) {
              const hip = Math.round(hipAttribute.getX(bestHit.index))
              this.handleStarClick(hip)
            }
          }
        }
      }
    }

    this.renderer.domElement.addEventListener('click', (e) => {
      handleClick(e.clientX, e.clientY)
    })
    this.renderer.domElement.addEventListener('touchend', (e) => {
      if (e.changedTouches.length > 0)
        handleClick(e.changedTouches[0].clientX, e.changedTouches[0].clientY)
    })
  }

  private updateSelectedStarIndicator(position: THREE.Vector3): void {
    if (!this.selectedStarIndicator) {
      const texture = this.createSelectionRingTexture()
      const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthWrite: false,
        depthTest: false,
      })
      this.selectedStarIndicator = new THREE.Sprite(material)
      this.selectedStarIndicator.renderOrder = 10
      this.scene.add(this.selectedStarIndicator)
    }

    this.selectedStarIndicator.position.copy(position)
    this.selectedStarIndicator.scale.setScalar(28)
    this.selectedStarIndicator.visible = true
  }

  private createSelectionRingTexture(): THREE.CanvasTexture {
    const size = 128
    const canvas = document.createElement('canvas')
    canvas.width = size
    canvas.height = size

    const ctx = canvas.getContext('2d')!
    const center = size / 2
    const radius = size * 0.35

    ctx.clearRect(0, 0, size, size)
    ctx.beginPath()
    ctx.arc(center, center, radius, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(255,255,255,0.95)'
    ctx.lineWidth = size * 0.06
    ctx.shadowColor = 'rgba(255,255,255,0.55)'
    ctx.shadowBlur = size * 0.06
    ctx.stroke()

    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    return texture
  }

  private clearSelectedStarIndicator(): void {
    if (!this.selectedStarIndicator) return

    this.scene.remove(this.selectedStarIndicator)
    const material = this.selectedStarIndicator.material
    if (material.map) material.map.dispose()
    material.dispose()
    this.selectedStarIndicator = null
  }

  private async handleStarClick(hip: number): Promise<void> {
    const starData = this.starMap.get(hip)

    if (starData && this.onStarClickCallback) {
      const { star, position } = starData
      this.updateSelectedStarIndicator(position)
      const nameData = getStarName(star.hIP)

      const rect = this.renderer.domElement.getBoundingClientRect()
      const screenPos = position.clone()
      screenPos.project(this.camera)
      const screenX = rect.left + (screenPos.x * 0.5 + 0.5) * rect.width
      const screenY = rect.top + (-(screenPos.y * 0.5 + 0.5) + 1) * rect.height

      let detailedData: any = {}

      const baseUrl = import.meta.env?.BASE_URL || '/'
      const cleanBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl

      try {
        const response = await fetch(`${cleanBase}/data/stars-data/HIP_${star.hIP}.json`)
        const contentType = response.headers.get('content-type')
        if (response.ok && contentType && contentType.indexOf('application/json') !== -1) {
          detailedData = await response.json()
        }
      } catch (error) {
        console.error(`Path star detail failed: ${star.hIP}`, error)
      }

      this.onStarClickCallback({
        hip: star.hIP,
        name: nameData?.chinese || `HIP ${star.hIP}`,
        englishName: nameData?.english || '',
        constellation: nameData?.constellation || 'Unknown',
        magnitude: star.magnitude,
        bvColor: star.bvColor,
        distance: star.distance,
        rightAscension: star.equatorialCoordinate.rightAscension,
        declination: star.equatorialCoordinate.declination,
        altitude: 0,
        azimuth: 0,
        screenX,
        screenY,
        originalName: detailedData.name || '',
        description: detailedData.description || '',
        url: detailedData.url || '',
        raw: detailedData,
      })
    }
  }

  private async startVideoStream(): Promise<void> {
    try {
      if (!this.videoElement) {
        this.videoElement = document.createElement('video')
        this.videoElement.setAttribute('playsinline', '')
        this.videoElement.setAttribute('webkit-playsinline', '')
        Object.assign(this.videoElement.style, {
          position: 'fixed',
          top: '0',
          left: '0',
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          zIndex: '-1',
          pointerEvents: 'none',
        })
        this.container.appendChild(this.videoElement)
      }

      // Request a very high-resolution rear camera stream; do NOT force screen aspect ratio.
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: { ideal: 'environment' },
          // prefer 4k, browser/device will negotiate down if unsupported
          width: { ideal: 3840 },
          height: { ideal: 2160 },
        } as any,
        audio: false,
      }

      this.videoStream = await navigator.mediaDevices.getUserMedia(constraints)

      this.videoElement.srcObject = this.videoStream
      await this.videoElement.play()

      // Try to read the actual video settings from the track (width/height/aspectRatio)
      const track = this.videoStream.getVideoTracks()[0]
      const settings = track.getSettings ? track.getSettings() : ({} as MediaTrackSettings)
      console.log('Video track settings:', settings)

      const videoStreamWidth = (settings.width as number) || this.videoElement.videoWidth
      const videoStreamHeight = (settings.height as number) || this.videoElement.videoHeight
      const videoStreamAspect = videoStreamWidth / videoStreamHeight

      // Adjust the video element's displayed width/height to match the actual video aspect
      if (this.videoElement) {
        const containerWidth = this.container.clientWidth || window.innerWidth
        const containerHeight = this.container.clientHeight || window.innerHeight
        const containerAspect = containerWidth / containerHeight
        if (videoStreamAspect > containerAspect) {
          Object.assign(this.videoElement.style, {
            width: '100%',
            height: 'auto',
            objectFit: 'contain',
          })
        } else {
          Object.assign(this.videoElement.style, {
            width: 'auto',
            height: '100%',
            objectFit: 'contain',
          })
        }
        console.log('Adjusted videoElement style to match actual video aspect', {
          actualAspect: videoStreamAspect,
          containerAspect,
        })
      }

      // Update renderer camera aspect to match video stream
      const fovInfo = this.getVideoStreamFov()
      console.log(
        `Video stream FOV: ${fovInfo.verticalFov.toFixed(2)}° (vertical), ${fovInfo.horizontalFov.toFixed(2)}° (horizontal) — source=${fovInfo.source}`,
      )

      this.camera = new THREE.PerspectiveCamera(
        fovInfo.verticalFov,
        videoStreamAspect,
        0.1,
        this.SKY_RADIUS * 2,
      )

      console.log('Camera started', {
        actualWidth: videoStreamWidth,
        actualHeight: videoStreamHeight,
        actualAspect: videoStreamAspect,
      })
    } catch (error) {
      console.error('Camera failed', error)
      throw error
    }
  }

  private stopCamera(): void {
    if (this.videoStream) {
      this.videoStream.getTracks().forEach((track) => track.stop())
      this.videoStream = null
    }
    if (this.videoElement) {
      this.videoElement.srcObject = null
      this.videoElement.remove()
      this.videoElement = null
    }
  }

  /**
   * Attempt to determine the video stream FOV (degrees).
   * Returns vertical and horizontal FOV plus a source hint, or null if no stream.
   * Tries several heuristics: physical focal length + sensor size (if exposed),
   * focal length in pixels, then falls back to using the renderer camera FOV
   * combined with the actual video aspect ratio.
   */
  public getVideoStreamFov(): {
    verticalFov: number
    horizontalFov: number
    source: string
  } {
    const track = this.videoStream!.getVideoTracks()[0]
    const settings: any = track.getSettings ? track.getSettings() : {}

    const toDeg = (r: number) => (r * 180) / Math.PI

    // 1) If settings expose physical focal length (mm) and sensor size (mm)
    if (settings.focalLength && (settings.sensorWidth || settings.sensorHeight)) {
      const focalMm = settings.focalLength // mm
      // prefer sensorHeight for vertical FOV; if absent, infer from sensorWidth and pixel aspect
      let sensorW = settings.sensorWidth
      let sensorH = settings.sensorHeight
      if (!sensorH && sensorW && settings.width && settings.height) {
        sensorH = (sensorW * settings.height) / settings.width
      }
      const vertical = sensorH ? toDeg(2 * Math.atan(sensorH / 2 / focalMm)) : NaN
      const horizontal = sensorW ? toDeg(2 * Math.atan(sensorW / 2 / focalMm)) : NaN
      return {
        verticalFov: Number.isFinite(vertical) ? vertical : this.camera.fov,
        horizontalFov: Number.isFinite(horizontal)
          ? horizontal
          : (2 *
              (Math.atan(
                Math.tan((this.camera.fov * Math.PI) / 360) *
                  (settings.aspectRatio || this.camera.aspect),
              ) *
                180)) /
            Math.PI,
        source: 'settings:focalLength+sensorSize',
      }
    }

    // 2) If focalLength is provided in pixels (some platforms), use it
    if (settings.focalLength && settings.width && settings.height) {
      const fPx = settings.focalLength // assume pixels
      const vertical = toDeg(2 * Math.atan(settings.height / 2 / fPx))
      const horizontal = toDeg(2 * Math.atan(settings.width / 2 / fPx))
      return {
        verticalFov: vertical,
        horizontalFov: horizontal,
        source: 'settings:focalLengthPixels',
      }
    }

    // 3) If we cannot obtain focal/sensor information, fail loudly —
    // this avoids silently returning an unreliable approximate FOV.
    console.error(
      'getVideoStreamFov: unable to determine FOV — track settings lack focal/sensor information',
    )
    // TODO: 根据手机屏拍预设 fov 的值，提供 UI 让用户调节fov的值
    return {
      verticalFov: 37.8,
      horizontalFov: 54.4,
      source: 'default',
    }
  }
}
