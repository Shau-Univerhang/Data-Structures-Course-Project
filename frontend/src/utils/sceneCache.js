class SceneCache {
  constructor() {
    this.cache = new Map()
    this.promiseCache = new Map()
  }

  get(key) {
    return this.cache.get(key) || null
  }

  set(key, sceneData) {
    this.cache.set(key, sceneData)
  }

  has(key) {
    return this.cache.has(key)
  }

  delete(key) {
    const sceneData = this.cache.get(key)
    if (sceneData) {
      this.disposeScene(sceneData)
    }
    this.cache.delete(key)
    this.promiseCache.delete(key)
  }

  disposeScene(sceneData) {
    if (sceneData.renderer) {
      sceneData.renderer.dispose()
    }
    if (sceneData.controls) {
      sceneData.controls.dispose()
    }
    if (sceneData.scene) {
      sceneData.scene.traverse((object) => {
        if (object.geometry) {
          object.geometry.dispose()
        }
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose())
          } else {
            object.material.dispose()
          }
        }
      })
    }
  }

  clear() {
    this.cache.forEach((sceneData) => {
      this.disposeScene(sceneData)
    })
    this.cache.clear()
    this.promiseCache.clear()
  }

  getOrCreate(key, createFn) {
    if (this.cache.has(key)) {
      return Promise.resolve(this.cache.get(key))
    }

    if (this.promiseCache.has(key)) {
      return this.promiseCache.get(key)
    }

    const promise = createFn().then((sceneData) => {
      this.cache.set(key, sceneData)
      this.promiseCache.delete(key)
      return sceneData
    }).catch((error) => {
      this.promiseCache.delete(key)
      throw error
    })

    this.promiseCache.set(key, promise)
    return promise
  }
}

export const sceneCache = new SceneCache()

export default SceneCache