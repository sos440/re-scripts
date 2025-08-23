# Memo

## Main

![Main](assets\gump_main.png)

```python
>>> gumpId:
3575701487

>>> gumpLayout:
{ resizepic 50 50 3600 200 150 }  # background
{ tilepic 45 45 3311 }   # vines
{ tilepic 45 118 3312 }   # vines
{ tilepic 211 45 3307 }   # vines
{ tilepic 211 118 3308 }   # vines
{ tilepichue 130 96 3206 43 }  # plant
{ tilepic 93 162 6809 }  # flax
{ tilepic 162 162 6809 }  # flax
{ xmfhtmlgumpcolor 129 167 42 20 1060822 0 0 33760 }  # "vibrant"
{ button 71 67 212 212 1 0 1 }  # Reproduction tab
{ tilepic 59 68 3336 }  # lily
{ button 71 91 212 212 1 0 2 }
{ tilepic 8 96 882 }
{ button 71 115 212 212 1 0 3 }
{ tilepic 58 115 3350 }
{ button 71 139 212 212 1 0 4 }
{ tilepic 59 143 6884 }
{ button 71 163 212 212 1 0 5 }
{ tilepic 55 167 5927 }
{ button 209 67 210 210 1 0 6 }  # water
{ tilepic 193 67 8093 }
{ text 196 67 33 0 }  # water status
{ button 209 91 212 212 1 0 7 }
{ tilepic 201 91 3850 }
{ text 196 91 2101 1 }
{ button 209 115 212 212 1 0 8 }
{ tilepic 201 115 3847 }
{ text 196 115 2101 1 }
{ button 209 139 212 212 1 0 9 }
{ tilepic 201 139 3852 }
{ text 196 139 2101 1 }
{ button 209 163 212 212 1 0 10 }
{ tilepic 201 163 3849 }
{ text 196 163 2101 1 }
{ gumppic 48 47 210 }
{ text 54 47 2101 2 }
{ gumppic 232 47 210 }
{ text 239 47 3 3 }
{ button 48 183 210 210 1 0 11 }
{ text 54 183 2101 4 }
{ tilepic 219 180 2323 }
{ button 232 183 212 212 1 0 12 }

>>> gumpData:
List[str](['3311', '3312', '3307', '3308', '6809', '6809', '3336', '882', '3350', '6884', '5927', '8093', '-', '3850', '0', '3847', '0', '3852', '0', '3849', '0', '9', '+', '?', '2323'])

>>> gumpDefinition:


>>> gumpStrings:
List[str]()

>>> gumpText:
List[str](['vibrant'])

```

## Reproduction tab

![Reproduction](assets/gump_reproduction.png)

```python
>>> gumpId:
3207983240

>>> gumpLayout:
{ resizepic 50 50 3600 200 150 }
{ gumppic 60 90 3607 }
{ gumppic 120 90 3607 }
{ gumppic 60 145 3607 }
{ gumppic 120 145 3607 }
{ tilepic 45 45 3311 }
{ tilepic 45 118 3312 }
{ tilepic 211 45 3307 }
{ tilepic 211 118 3308 }
{ button 70 67 212 212 1 0 1 }
{ tilepic 57 65 5632 }
{ text 108 67 2101 0 }
{ button 212 67 212 212 1 0 2 }
{ tilepic 202 68 3169 }
{ text 216 66 33 1 }
{ button 80 116 212 212 1 0 3 }
{ tilepic 66 117 6818 }
{ text 106 116 63 2 }
{ button 128 116 212 212 1 0 4 }
{ tilepic 113 120 4129 }
{ text 149 116 43 3 }
{ button 177 116 212 212 1 0 5 }
{ tilepic 160 121 3535 }
{ text 199 116 43 3 }
{ button 70 163 210 210 1 0 6 }
{ tilepic 56 164 6818 }
{ button 138 163 210 210 1 0 7 }
{ tilepic 123 167 4129 }
{ button 212 163 210 210 1 0 8 }
{ tilepic 195 168 3535 }

>>> gumpData:
List[str](['3311', '3312', '3307', '3308', '5632', 'Reproduction', '3169', '/', '6818', '+', '4129', '8/8', '3535', '8/8', '6818', '4129', '3535'])

>>> gumpDefinition:


>>> gumpStrings:
List[str]()

>>> gumpText:
List[str]()

```

## Confirm

![Confirm](assets/gump_confirm.png)

```python
>>> gumpId:
3709352399

>>> gumpLayout:
{ resizepic 50 50 3600 200 150 }
{ tilepic 25 45 3307 }
{ tilepic 25 118 3308 }
{ tilepic 227 45 3311 }
{ tilepic 227 118 3312 }
{ text 115 85 68 0 }
{ text 82 105 68 1 }
{ button 98 140 1150 1152 1 0 1 }
{ button 138 141 210 210 1 0 2 }
{ text 143 141 2101 2 }
{ button 168 140 1153 1155 1 0 3 }

>>> gumpData:
List[str](['3307', '3308', '3311', '3312', 'Set plant', 'to decorative mode?', '?'])

>>> gumpDefinition:


>>> gumpStrings:
List[str]()

>>> gumpText:
List[str]()
```
