import type { StarMeta } from './star-meta'

// 原始 JSON 数据格式
interface RawStarData {
  hip: number
  alpha: number
  delta: number
  mag: number
  pmRA: number
  pmDE: number
  bvColor: number
  distance: number
}

/**
 * 将原始 JSON 数据转换为 StarMeta 格式
 */
function convertToStarMeta(raw: RawStarData): StarMeta {
  const distance = raw.distance != null && raw.distance >= 0 ? raw.distance : undefined
  return {
    hIP: raw.hip,
    equatorialCoordinate: {
      rightAscension: raw.alpha,
      declination: raw.delta,
    },
    magnitude: raw.mag,
    pmRA: raw.pmRA,
    pmDE: raw.pmDE,
    bvColor: raw.bvColor,
    distance: distance,
  }
}

// 模块级缓存
let starCatalogCache: StarMeta[] | null = null
let loadingPromise: Promise<StarMeta[]> | null = null

/**
 * 加载星表数据（带缓存，只会加载一次）
 */
async function loadStarCatalog(): Promise<StarMeta[]> {
  // 如果已经加载过，直接返回缓存
  if (starCatalogCache !== null) {
    return starCatalogCache
  }
  // 如果正在加载中，返回同一个 Promise（避免并发重复加载）
  if (loadingPromise !== null) {
    return loadingPromise
  }

  // 浏览器环境
  loadingPromise = fetch('/data/star-catalog/star-catalog.json')
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Failed to load star catalog: ${response.status}`)
      }
      const data = await response.json()
      starCatalogCache = (data as RawStarData[]).map(convertToStarMeta)
      return starCatalogCache
    })
    .catch((error) => {
      console.error('Error loading star catalog:', error)
      loadingPromise = null // 失败后重置，允许重试
      throw error
    })
  return loadingPromise
}

/**
 * 获取已缓存的星表数据（同步）
 * 如果未加载，返回 null
 */
function getStarCatalogSync(): StarMeta[] | null {
  return starCatalogCache
}

/**
 * 清除缓存（用于测试或强制重新加载）
 */
function clearStarCatalogCache(): void {
  starCatalogCache = null
  loadingPromise = null
}

// 导出接口统一放到文件末尾
export { loadStarCatalog, getStarCatalogSync, clearStarCatalogCache }
