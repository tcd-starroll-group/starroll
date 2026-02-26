import * as THREE from 'three'
import type { StarMeta } from '../../../../../gen/ts/models/StarMeta'
import type { GPS } from '../../../../../gen/ts/models/GPS'
import { loadStarCatalog } from '../astronomy/star-catalog'
import { getStarName } from '../data/star-names'
import { absoluteOrientationManager, AbsoluteOrientationData } from '../sensors/AbsoluteOrientation'
import { raDecToVector3 } from '../astronomy/cartesian-coordinate'
import { convertHorizontalQuaternionToEquatorialQuaternionPro } from '../astronomy/astronomy'

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

/**
 * Ground Observer Renderer
 * Simulates sky view from Earth surface
 */
export class GroundObserverRenderer {
  // millisecond
  public timestamp: number = 1772069929000
  public location: GPS = { longitude: -6.2603, latitude: 53.3498 }
  //  { longitude: -6.2603, latitude: 53.3498 }

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

  // Celestial sphere
  private readonly SKY_RADIUS = 1000

  // Animation
  private animationFrameId: number | null = null

  // AR mode
  private arMode: boolean = false

  private absoluteOrientation: [number, number, number, number] | null = null // 四元数数据

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
    this.scene.background = new THREE.Color(0x000510)

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
    })
    this.renderer.setSize(window.innerWidth, window.innerHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.0
    container.appendChild(this.renderer.domElement)

    // this.createGround();
    // this.createHorizon();
    this.setupLighting()

    this.loadStarField()
    this.animate()
    this.setupClickDetection()

    window.addEventListener('resize', this.onWindowResize)
    window.addEventListener('orientationchange', () => {
      setTimeout(this.onWindowResize, 200)
    })

    absoluteOrientationManager.addListener((quaternion: AbsoluteOrientationData) => {
      this.absoluteOrientation = quaternion.quaternion
      this.updateARCameraLookAt()
    })
    absoluteOrientationManager.startListening()

    console.log('Ground Observer Renderer initialized')
  }

  // 更新AR渲染时的lookat
  private updateARCameraLookAt() {
    if (this.absoluteOrientation) {
      const [x, y, z, w] = this.absoluteOrientation
      // Convert horizontal quaternion to equatorial quaternion for camera
      let ans = convertHorizontalQuaternionToEquatorialQuaternionPro(
        [x, y, z, w],
        this.timestamp,
        this.location,
      )
      this.camera.quaternion.set(ans[0], ans[1], ans[2], ans[3])
      // Also convert the raw absolute orientation quaternion to Euler angles and log
      // const deviceQuat = new THREE.Quaternion(x, y, z, w)
      // const euler = new THREE.Euler().setFromQuaternion(deviceQuat, 'ZYX')
      // const radToDeg = (r: number) => (r * 180) / Math.PI
      // console.log('absoluteOrientation (quaternion):', [x, y, z, w], '-> euler (deg):', {
      //   x: Number(radToDeg(euler.x).toFixed(2)),
      //   y: Number(radToDeg(euler.y).toFixed(2)),
      //   z: Number(radToDeg(euler.z).toFixed(2)),
      // })
    } else {
      console.error('GroundObserverRenderer: no absoluteOrientation available')
    }
  }

  /**
   * Create ground plane with fade-out grid
   */
  private createGround(): void {
    const geometry = new THREE.CircleGeometry(2000, 64)
    const material = new THREE.ShaderMaterial({
      uniforms: {
        uColor: { value: new THREE.Color(0x0a0a15) },
      },
      vertexShader: `
                varying vec2 vUv;
                varying vec3 vPosition;
                void main() {
                    vUv = uv;
                    vPosition = position;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
      fragmentShader: `
                uniform vec3 uColor;
                varying vec2 vUv;
                varying vec3 vPosition;
                void main() {
                    float dist = length(vPosition);
                    float fade = 1.0 - smoothstep(1000.0, 2000.0, dist);
                    float grid = 0.0;
                    float gridSize = 100.0;
                    if (mod(vPosition.x, gridSize) < 2.0 || mod(vPosition.y, gridSize) < 2.0) {
                        grid = 0.05;
                    }
                    vec3 color = uColor + vec3(grid);
                    gl_FragColor = vec4(color, fade);
                }
            `,
      transparent: true,
      side: THREE.DoubleSide,
    })
    this.ground = new THREE.Mesh(geometry, material)
    this.ground.rotation.x = -Math.PI / 2
    this.ground.position.y = 0
    this.scene.add(this.ground)
  }

  /**
   * Create horizon circle line
   */
  private createHorizon(): void {
    const points: THREE.Vector3[] = []
    const segments = 128
    const horizonRadius = 1500
    for (let i = 0; i <= segments; i++) {
      const angle = (i / segments) * Math.PI * 2
      const x = Math.cos(angle) * horizonRadius
      const z = Math.sin(angle) * horizonRadius
      points.push(new THREE.Vector3(x, 0, z))
    }
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({
      color: 0x4488ff,
      transparent: true,
      opacity: 0.3,
    })
    this.horizon = new THREE.Line(geometry, material)
    this.scene.add(this.horizon)
  }

  private setupLighting(): void {
    const ambientLight = new THREE.AmbientLight(0x202040, 0.2)
    this.scene.add(ambientLight)
  }

  private async loadStarField(): Promise<void> {
    try {
      console.log('Loading star catalog...')
      const stars = await loadStarCatalog()
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
    }[] = []
    const mediumStars: {
      pos: THREE.Vector3
      color: THREE.Color
      star: StarMeta
    }[] = []
    const dimStars: {
      pos: THREE.Vector3
      color: THREE.Color
      star: StarMeta
    }[] = []

    this.starMap.clear()

    stars.forEach((star) => {
      if (star.magnitude > 4.5) return

      const pos = raDecToVector3(
        star.equatorialCoordinate.rightAscension,
        star.equatorialCoordinate.declination,
        this.SKY_RADIUS,
      )
      const color = this.bvToRGB(star.bvColor)
      this.starMap.set(star.hIP, { star, position: pos })

      const starData = { pos, color, star }
      if (star.magnitude < 1.0) brightStars.push(starData)
      else if (star.magnitude < 2.5) mediumStars.push(starData)
      else dimStars.push(starData)
    })

    if (this.starPoints) this.scene.remove(this.starPoints)

    const starGroup = new THREE.Group()
    starGroup.name = 'Stars'

    if (brightStars.length > 0)
      starGroup.add(this.createStarPoints(brightStars, '/texture/star16x16_ray.png', 8.0))
    if (mediumStars.length > 0)
      starGroup.add(this.createStarPoints(mediumStars, '/texture/star16x16.png', 5.0))
    if (dimStars.length > 0)
      starGroup.add(this.createStarPoints(dimStars, '/texture/star16x16.png', 3.0))

    this.starPoints = starGroup as any
    this.scene.add(starGroup)
  }

  private createStarPoints(
    starsData: { pos: THREE.Vector3; color: THREE.Color; star: StarMeta }[],
    texturePath: string,
    baseSize: number,
  ): THREE.Points {
    const positions: number[] = []
    const colors: number[] = []
    const magnitudes: number[] = []
    const twinklePhases: number[] = []
    const hips: number[] = []

    starsData.forEach(({ pos, color, star }) => {
      positions.push(pos.x, pos.y, pos.z)
      colors.push(color.r, color.g, color.b)
      magnitudes.push(star.magnitude)
      twinklePhases.push(Math.random() * Math.PI * 2)
      hips.push(star.hIP)
    })

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
    geometry.setAttribute('magnitude', new THREE.Float32BufferAttribute(magnitudes, 1))
    geometry.setAttribute('twinklePhase', new THREE.Float32BufferAttribute(twinklePhases, 1))
    geometry.setAttribute('hip', new THREE.Float32BufferAttribute(hips, 1))

    const isRayTexture = texturePath.includes('ray')
    const texture = this.createProceduralStarTexture(isRayTexture)
    const material = this.createTwinkleStarMaterial(texture, baseSize)

    return new THREE.Points(geometry, material)
  }

  private createTwinkleStarMaterial(
    texture: THREE.Texture,
    baseSize: number,
  ): THREE.ShaderMaterial {
    return new THREE.ShaderMaterial({
      uniforms: {
        uTexture: { value: texture },
        uSize: { value: baseSize },
        uTime: { value: 0 },
        uPixelRatio: { value: window.devicePixelRatio },
      },
      vertexShader: `
                attribute vec3 color;
                attribute float magnitude;
                attribute float twinklePhase;
                uniform float uSize;
                uniform float uTime;
                uniform float uPixelRatio;
                varying vec3 vColor;
                varying float vTwinkle;
                void main() {
                    vColor = color;
                    float twinkleSpeed = 1.0 + magnitude * 0.3;
                    float twinkleAmount = 0.15 + (6.0 - magnitude) * 0.05;
                    float twinkle = sin(uTime * twinkleSpeed + twinklePhase) * twinkleAmount;
                    vTwinkle = 1.0 + twinkle;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_Position = projectionMatrix * mvPosition;
                    gl_PointSize = uSize * vTwinkle * uPixelRatio;
                }
            `,
      fragmentShader: `
                uniform sampler2D uTexture;
                varying vec3 vColor;
                varying float vTwinkle;
                void main() {
                    vec4 texColor = texture2D(uTexture, gl_PointCoord);
                    vec3 finalColor = texColor.rgb * vColor * vTwinkle;
                    float alpha = texColor.a;
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

  private bvToRGB(bv: number): THREE.Color {
    let r: number, g: number, b: number
    if (bv < 0) {
      r = 0.7
      g = 0.8
      b = 1.0
    } else if (bv < 0.5) {
      const t = bv / 0.5
      r = 0.8 + t * 0.2
      g = 0.9 + t * 0.1
      b = 1.0 - t * 0.1
    } else if (bv < 1.0) {
      const t = (bv - 0.5) / 0.5
      r = 1.0
      g = 1.0 - t * 0.15
      b = 0.9 - t * 0.25
    } else if (bv < 1.5) {
      const t = (bv - 1.0) / 0.5
      r = 1.0
      g = 0.85 - t * 0.2
      b = 0.65 - t * 0.25
    } else {
      r = 1.0
      g = 0.65
      b = 0.4
    }
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

    this.scene.background = new THREE.Color(0x000510)
    if (this.ground) this.ground.visible = true
    if (this.horizon) this.horizon.visible = true
    console.log('AR mode disabled')
  }

  /**
   * Main render loop with adaptive AR smoothing
   */
  private animate = () => {
    const time = Date.now() * 0.001 // second

    if (this.starPoints) {
      this.starPoints.traverse((child: any) => {
        if (child instanceof THREE.Points && child.material instanceof THREE.ShaderMaterial) {
          child.material.uniforms.uTime.value = time
        }
      })
    }

    this.renderer.render(this.scene, this.camera)
    this.animationFrameId = requestAnimationFrame(this.animate)
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
    if (this.animationFrameId) cancelAnimationFrame(this.animationFrameId)
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
