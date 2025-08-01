import numpy as np


class TrustElement:
    def __init__(self,ast_data,ob_data,ds_data,ap_data,at_data):
        self.InitTrust = 0

        self.AST_NumAS = ast_data['num_as']
        self.AST_NumAF = ast_data['num_af']

        self.OB_NumView = ob_data['num_view']
        self.OB_NumCopy = ob_data['num_copy']
        self.OB_NumDownload = ob_data['num_download']
        self.OB_NumAdd = ob_data['num_add']
        self.OB_NumRevise = ob_data['num_revise']
        self.OB_NumDelete = ob_data['num_delete']
        self.OB_a = 0.3
        self.OB_b = 0.3
        self.OB_c = 0.4

        self.DS_Num1 = ds_data['num1']
        self.DS_Num2 = ds_data['num2']
        self.DS_Num3 = ds_data['num3']
        self.DS_Num4 = ds_data['num4']
        self.DS_a = 1.
        self.DS_b = 1.
        self.DS_c = 1.
        self.DS_d = 1.

        self.AP_NumNI = ap_data['num_ni']
        self.AP_NumUI = ap_data['num_ui']

        self.AT_NumND = at_data['num_nd']
        self.AT_NumAD = at_data['num_ad']

        self.RootLeaves = 100
        self.DPLeaves = [1, 2, 3]
        self.DPSubsumers = [4, 5, 6]
        self.DQLeaves = [7, 8, 9, 3]
        self.DQSubsumers = [5, 6, 7, 9]
        self.LCALeaves = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.LCASubsumers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


class TrustValue:
    def __init__(self, TrustElement: TrustElement):
        self.Trustelement = TrustElement
        self.AST = 0.
        self.OB = 0.
        self.DS = 0.
        self.AP = 0.
        self.AT = 0.
        self.SS = 0.
        self.W = [0.26666667, 0.23333333, 0.13333333, 0.3, 0.03333333, 0.03333333]
        self.Uncertain = 0.75

    def ASTValue(self):
        self.AST = self.Trustelement.AST_NumAS * 1. / (self.Trustelement.AST_NumAS + self.Trustelement.AST_NumAF)

    def OBValue(self):
        OBWeightedSum = self.Trustelement.OB_NumView * self.Trustelement.OB_a + \
                        (self.Trustelement.OB_NumCopy + self.Trustelement.OB_NumDownload) * self.Trustelement.OB_b + \
                        (
                                self.Trustelement.OB_NumAdd + self.Trustelement.OB_NumRevise + self.Trustelement.OB_NumDelete) * self.Trustelement.OB_c
        OBNumSum = self.Trustelement.OB_NumView + self.Trustelement.OB_NumCopy + self.Trustelement.OB_NumDownload + \
                   self.Trustelement.OB_NumAdd + self.Trustelement.OB_NumRevise + self.Trustelement.OB_NumDelete
        self.OB = 1 - OBWeightedSum / OBNumSum

    def DSValue(self):
        DSWeightedSum = self.Trustelement.DS_Num1 * self.Trustelement.DS_a + self.Trustelement.DS_Num2 * self.Trustelement.DS_b + \
                        self.Trustelement.DS_Num3 * self.Trustelement.DS_c + self.Trustelement.DS_Num4 * self.Trustelement.DS_d
        DSNumSum = self.Trustelement.DS_Num1 + self.Trustelement.DS_Num2 + self.Trustelement.DS_Num3 + self.Trustelement.DS_Num4
        self.DS = 1 - DSWeightedSum / DSNumSum

    def APValue(self):
        self.AP = self.Trustelement.AP_NumNI * 1. / (self.Trustelement.AP_NumNI + self.Trustelement.AP_NumUI)

    def ATValue(self):
        self.AT = self.Trustelement.AT_NumND * 1. / (self.Trustelement.AT_NumND + self.Trustelement.AT_NumAD)

    def IC(self, leavesD, subsumersD, leavesR):
        up = leavesD * 1. / subsumersD + 1
        dowm = leavesR * 1. + 1
        return -np.log(up / dowm)

    def CS(self, ICP, ICQ, ICLCA):
        return 2. * ICLCA / ICP / ICQ

    def SSValue(self):
        LenthP = len(self.Trustelement.DPLeaves)
        LenthQ = len(self.Trustelement.DQLeaves)
        leavesR = self.Trustelement.RootLeaves

        SumP = 0.
        for i in range(LenthP):
            ICP = self.IC(self.Trustelement.DPLeaves[i], self.Trustelement.DPSubsumers[i], leavesR)
            MinP = 100.
            for j in range(LenthQ):
                ICQ = self.IC(self.Trustelement.DQLeaves[j], self.Trustelement.DQSubsumers[j], leavesR)
                ICLCA = self.IC(self.Trustelement.LCALeaves[i * LenthQ + j],
                                self.Trustelement.LCASubsumers[i * LenthQ + j], leavesR)
                MinP = min(MinP, self.CS(ICP*1., ICQ*1., ICLCA*1.))
            SumP = SumP + MinP

        SumQ = 0.
        for i in range(LenthQ):
            ICQ = self.IC(self.Trustelement.DQLeaves[i], self.Trustelement.DQSubsumers[i], leavesR)
            MinQ = 100.
            for j in range(LenthP):
                ICP = self.IC(self.Trustelement.DPLeaves[j], self.Trustelement.DPSubsumers[j], leavesR)
                ICLCA = self.IC(self.Trustelement.LCALeaves[j * LenthQ + i],
                                self.Trustelement.LCASubsumers[j * LenthQ + i], leavesR)
                MinQ = min(MinQ, self.CS(ICP*1., ICQ*1., ICLCA*1.))
            SumQ = SumQ + MinQ

        return 1. - (SumP + SumQ) / (LenthQ + LenthP)

    def GetValue(self):
        self.ASTValue()
        self.OBValue()
        self.DSValue()
        self.APValue()
        self.ATValue()
        self.SSValue()
        # return 1.
        TrValue = self.AST * self.W[0] + self.OB * self.W[1] + self.DS * self.W[2] + \
                  self.AP * self.W[3] + self.AT * self.W[4] + self.SS * self.W[5]
        return TrValue

        # ITrValue = (TrValue, (1. - TrValue ** self.Uncertain) ** (1 / self.Uncertain))
        # return ITrValue


class TrustTreshold:
    def __init__(self, ):
        self.Uncertain = 0.75
        # self.Pi1 = 0.1
        # self.Pi2 = 0.1
        self.S_Tres = [-0.18260, 0.489701, 0.7392423, 0.9669546, 0.9629972]
        self.Tres = [[0.23382, 0.41435], [0.60047, 0.13693], [0.75024, 0.06846], [0.90070, 0.01889], [0.92951, 0.01184]]

    def S_ITrV(self, TrusV, uTrusV):
        return TrusV - uTrusV + (TrusV - uTrusV) ** 3 * (1-TrusV - uTrusV)

    def S_ITrT(self, TrusT, uTrusT):
        return TrusT - uTrusT + (TrusT - uTrusT) ** 3 * (1-TrusT - uTrusT)
