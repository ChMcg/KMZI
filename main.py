from aes.aes import AES, Key
from aes.aes_other import Matrix


text = Matrix.from_string('bakhir_andrey')
key = Key.from_string('7361_dmitrievich')

print('Ключ:')
print(key)

keys = key.generate_keys()
print(keys)
