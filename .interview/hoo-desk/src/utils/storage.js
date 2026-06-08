let storage = window.localStorage
export function getStorage (key) {
  return storage.getItem(key)
}

export function setStorage (key, value) {
  if (value === '' || value === []) {
    return storage.removeItem(key)
  } else {
    return storage.setItem(key, value)
  }
}

export function removeStorage (key) {
  return storage.removeItem(key)
}


