class Space:
    def __init__(self, cx, cy, cz, w, l, h):
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.w = w
        self.l = l
        self.h = h

class OctetTree:
    def __init__(self, Space, profondeur=0):
        self.figure = Space  #(cx, cy, cz, w, l, h)
        self.sousregion = [None, None, None, None, None, None, None, None]
        self.profondeur = profondeur
        self.nb_noeud = 0 # le nombre de noeuds que chaque parent possède

    def insert(self, n):
        # la localisation des noeuds
        if n.z > self.figure.cz:
            if n.x < self.figure.cx:
                # space 1
                if n.y > self.figure.cy:
                    if self.sousregion[0] is None:
                        self.sousregion[0] = n
                    else:
                        figure = Space(self.figure.cx - self.figure.w / 4,
                                       self.figure.cy + self.figure.l / 4,
                                       self.figure.cz + self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[0]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[0] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[0].insert(existant)
                            self.sousregion[0].insert(n)
                # space 2
                else:
                    if self.sousregion[1] is None:
                        self.sousregion[1] = n
                    else:
                        figure = Space(self.figure.cx - self.figure.w / 4,
                                       self.figure.cy - self.figure.h / 4,
                                       self.figure.cz + self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[1]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[1] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[1].insert(existant)
                            self.sousregion[1].insert(n)
            else:
                # space 3
                if n.y > self.figure.cy:
                    if self.sousregion[2] is None:
                        self.sousregion[2] = n
                    else:
                        figure = Space(self.figure.cx + self.figure.w / 4,
                                       self.figure.cy + self.figure.l / 4,
                                       self.figure.cz + self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[2]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[2] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[2].insert(existant)
                            self.sousregion[2].insert(n)
                # space 4
                else:
                    if self.sousregion[3] is None:
                        self.sousregion[3] = n
                    else:
                        figure = Space(self.figure.cx + self.figure.w / 4,
                                       self.figure.cy - self.figure.h / 4,
                                       self.figure.cz + self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[3]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[3] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[3].insert(existant)
                            self.sousregion[3].insert(n)
        else:
            if n.x < self.figure.cx:
                # space 5
                if n.y > self.figure.cy:
                    if self.sousregion[4] is None:
                        self.sousregion[4] = n
                    else:
                        figure = Space(self.figure.cx - self.figure.w / 4,
                                       self.figure.cy + self.figure.l / 4,
                                       self.figure.cz - self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[4]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[4] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[4].insert(existant)
                            self.sousregion[4].insert(n)
                # space 6
                else:
                    if self.sousregion[5] is None:
                        self.sousregion[5] = n
                    else:
                        figure = Space(self.figure.cx - self.figure.w / 4,
                                       self.figure.cy - self.figure.h / 4,
                                       self.figure.cz - self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[5]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[5] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[5].insert(existant)
                            self.sousregion[5].insert(n)
            else:
                # space 7
                if n.y > self.figure.cy:
                    if self.sousregion[6] is None:
                        self.sousregion[6] = n
                    else:
                        figure = Space(self.figure.cx + self.figure.w / 4,
                                       self.figure.cy + self.figure.l / 4,
                                       self.figure.cz - self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[6]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[6] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[6].insert(existant)
                            self.sousregion[6].insert(n)
                # space 8
                else:
                    if self.sousregion[7] is None:
                        self.sousregion[7] = n
                    else:
                        figure = Space(self.figure.cx + self.figure.w / 4,
                                       self.figure.cy - self.figure.h / 4,
                                       self.figure.cz - self.figure.h / 4,
                                       self.figure.w / 2,
                                       self.figure.l / 2,
                                       self.figure.h / 2)
                        existant = self.sousregion[7]
                        if isinstance(existant, OctetTree):
                            existant.insert(n)
                        # si existant est un noeud, il est remplacé par un nouveau OctetTree et il se situe dans ce OctetTree.
                        else:
                            self.sousregion[7] = OctetTree(figure, profondeur=self.profondeur + 1)
                            self.sousregion[7].insert(existant)
                            self.sousregion[7].insert(n)

        self.nb_noeud += 1