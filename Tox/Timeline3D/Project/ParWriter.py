import json

class ParWriter:
    def __init__(self, comp):
        self.targetOp = comp
        pages = self.targetOp.customPages
        self.ParInfo = {k.name: k.pars for k in pages}

    def GetPars(self, excludePages = [None]):
        parInfo = self.ParInfo.copy()
        for i in excludePages:
            if i != None and i in parInfo:
                parInfo.pop(i)
        return parInfo

    def __getitem__(self, page):
        return self.ParInfo[page]
    
    def ConvertToJsonable(self, excludePages = set()):
        oldPages = set(self.ParInfo.keys())
        difPages = oldPages - excludePages
        savableDict = dict()
        for i in difPages:
            savableDict[i] = [self.GetParValue(x) for x in self.ParInfo.get(i, [])]
        return savableDict

    def UpdatePars(self, jsonString = None, jsonDict = None):
        if jsonString:
            dataDict = json.loads(jsonString)
        elif jsonDict:
            dataDict = jsonDict
        else:
            dataDict = None
            print('Failed to pass data to update')
            return False

        for key, parList in dataDict.items():
            for iPar in self.ParInfo.get(key, []):
                for jPar in parList:
                    if iPar.name == jPar[0]:
                        self.SetParValue(iPar, jPar)
        return True

    def GetParValue(self, curPar):
        parMode = curPar.mode
        if parMode == ParMode.EXPRESSION:
            val = (curPar.name, 'expr', curPar.expr)
        elif parMode == ParMode.CONSTANT:
            val = (curPar.name, 'const', curPar.val)
        else:
            val = (curPar.name, 'const', curPar.eval())
        return val

    def SetParValue(self, oldPar, newParTuple):
        if len(newParTuple) < 3:
            return False
        if newParTuple[1] == 'expr':
            oldPar.expr = newParTuple[2]
            return True
        elif newParTuple[1] == 'const':
            oldPar.val = newParTuple[2]
            return True
        else:
            return False
