import pymel.all as pm
from MARS.MarsNode import MarsNode
import MARS.MarsUtilities as mu
reload(mu)

class MultiConstraint(MarsNode):
    def __init__(self,anim,influences,translation = True,rotation = True,node = None):
        if node != None: self.node = node
        else: self.node = self.exist_check('MultiConstraint',anim,'constraint_anim')
        
        if self.node == None:
            #Run Function
            MarsNode.__init__(self,'','MultiConstraint')
            
            #Variables
            name = self.node.name()
            if not isinstance(influences,list): influences = [influences]
            influences = [pm.PyNode(x) for x in influences]
            influence_nulls = []
            anim = pm.PyNode(anim)
            hidden_grp = pm.listConnections(list(set(pm.listConnections(anim.connected_to)))[0].hidden_grp)[0]
            lock_attrs = [str(x) for x in pm.listAttr(anim,l = True,st = ['translate*','rotate*','scale*'])]
            
            #Null
            for at in lock_attrs: anim.attr(at).unlock()
            null = mu.stack_chain(anim,rep = '_anim',wi = '_multicon_null',separate = False)[0]
            for at in lock_attrs: anim.attr(at).lock()
            
            #Attr Setup
            en = ''
            attributes = []
            for i, inf in enumerate(influences):
                en = en + inf.name() + ':'
                con_obj = pm.group(n = self.node.name() + '_' + inf + '_null',em = True)
                influence_nulls.append(con_obj)
                mu.aligner(con_obj,null)
                w = 0
                if i == 0: w = 1
                if translation == True: trans_con = pm.pointConstraint(con_obj, null,w = w, mo=True)
                if rotation == True: rot_con = pm.orientConstraint(con_obj, null, w = w, mo=True)
                pm.parentConstraint(inf,con_obj,mo = True)
                attributes.append(con_obj + 'W' + str(i))
            
            anim.addAttr('parent_to',at = 'enum',en = en,dv = 0,k = True)
            
            for i, at in enumerate(attributes):
                cond = mu.create_node('condition',n=(name + '_condition_' + str(i + 1)))
                anim.parent_to >> cond.firstTerm
                cond.secondTerm.set(i)
                cond.colorIfTrue.set(1,1,1)
                cond.colorIfFalse.set(0,0,0)
                if translation == True: cond.outColorR >> trans_con.attr(at)
                if rotation == True: cond.outColorR >> rot_con.attr(at)
            
            #Finalize
            pm.parent(influence_nulls,hidden_grp)
            
            ##Assign To Node
            self.node.addAttr('parent_index',at = 'byte',min = 0, max = (len(influences) - 1))
            anim.parent_to >> self.node.parent_index
            mu.con_link(anim,self.node,'constraint_anim')
            mu.con_link(null,self.node,'null')
            mu.con_link(influences,self.node,'influences')
            mu.con_link(influence_nulls,self.node,'influence_nulls')