import pymel.all as pm
from MARS.MarsRigComponent import MarsRigComponent
import MARS.MarsUtilities as mu
reload(mu)

class FKIKLimb(MarsRigComponent):
    def __init__(self,type,side,limb,start,end):
        #Run Function
        MarsRigComponent.__init__(self,type, side, limb, start = start, end = end)
        
    def get_FK_anim_grp(self):
        if self.node.hasAttr('FK_anim_grp'): return pm.listConnections(self.node.FK_anim_grp)[0]
    
    def get_IK_anim_grp(self):
        if self.node.hasAttr('IK_anim_grp'): return pm.listConnections(self.node.IK_anim_grp)[0]
        
    def get_switch(self):
        return pm.listConnections(self.node.switch)[0]
    
    def FKIK_anim_visibility(self,switch,IK_grp,FK_grp):
        name = switch.name().replace('_switch','')
        
        anim_rev = mu.create_node('reverse', n = name + '_anim_vis_reverse')
        anim_md = mu.create_node('multiplyDivide', n = name + '_anim_vis_multiply')
        anim_range = mu.create_node('setRange', n = name + '_anim_vis_range')
            
        anim_md.input2.set(100,100,100)
        anim_range.max.set(1,1,1)
        anim_range.oldMax.set(1,1,1)
            
        switch.FKIK_switch >> anim_rev.inputX
        switch.FKIK_switch >> anim_md.input1X
        anim_rev.outputX >> anim_md.input1Y
        anim_md.output >> anim_range.value
            
        anim_range.outValueX >> IK_grp.visibility
        anim_range.outValueY >> FK_grp.visibility
    
    def FKIK_stretch_blend(self, switch, controls, FK_nodes, IK_nodes, stretch_type, attribute = 'FKIK_switch'):
        for i, c in enumerate(controls[:-1]):
            bc = mu.create_node('blendColors',c + '_stretch_bl')
            FK_nodes[i].outputX >> bc.color2R
            IK_nodes[i].outputX >> bc.color1R
            switch.attr(attribute) >> bc.blender
            if stretch_type == 'position': bc.outputR >> controls[i + 1].tx
            else: bc.outputR >> controls[i].sx
    
    def IK_spline_stretch_setup(self,chain,cv,stretch_type):
        distances = []
        locators = []
        mds = []
        nurb_nulls = []
        length = mu.get_bone_length(chain[0],chain[-1])
        type = cv.getShape().nodeType()
    
        for i, x in enumerate(chain[:-1]):
            distances.append(pm.distanceDimension(sp = (0,i,0),ep = (0,i + 1,0)))
            loc = pm.PyNode('locator' + str(i + 1)).rename(x + '_locator')
            locators.append(loc)
            mu.aligner(loc,x)
        loc = pm.PyNode('locator' + str(len(chain))).rename(chain[-1] + '_locator')
        locators.append(loc)
        mu.aligner(loc,chain[-1])
    
        amnt = 0.00
        for i, loc in enumerate(locators):
            if i > 0 and i != len(chain) - 1: amnt += mu.get_bone_length(chain[i - 1],chain[i])/length
            elif i == len(chain) - 1: amnt = 1.00
            if type == 'nurbsCurve': mu.curve_constraint(cv,loc,amnt)
            else: nurb_nulls.append(mu.nurbs_constraint(cv,loc,u = 0.5, v = amnt))
        
        for i, dist in enumerate(distances):
            dist.addAttr('default',at = 'double',dv = dist.distance.get())
            dist.default.lock()
            rmd = mu.create_node('multiplyDivide', n = chain[i] + '_global_md')
            md = mu.create_node('multiplyDivide', n = chain[i] + '_md')
            dist.distance >> rmd.input1X
            self.node.global_scale >> rmd.input2X
            rmd.operation.set(2)
            rmd.outputX >> md.input1X
            if chain[i + 1].tx.get() < 0: md.input2X.set(-1)
            else: md.input2X.set(1)

            if stretch_type == 'scale':
                stretch = mu.create_node('multiplyDivide', n = chain[i] + '_stretch_md')
                md.outputX >> stretch.input1X
                stretch.input2X.set(stretch.input1X.get())
                stretch.operation.set(2)
                stretch.outputX >> chain[i].sx
                mds.append(stretch)
            else:
                md.outputX >> chain[i + 1].tx
                mds.append(md)
            
        if type == 'nurbsCurve': return mds, locators, distances
        else: return mds, locators, distances, nurb_nulls
    
    def IK_roll_attribute_setup(self,name,IK_anim,pivots):
        #Variables
        back = pivots[0]
        inner = pivots[1]
        outer = pivots[2]
        front = pivots[3]
        center = pivots[4]
        digit = pivots[6]
        
        #Attributes
        IK_anim.addAttr('heel_to_toe',at = 'double',min = -180,max = 180,dv = 0,k = True)
        IK_anim.addAttr('balltoe_lift',at = 'double',min = -180, max = 180, dv= 0, k = True)
        IK_anim.addAttr('toe_lift',at = 'double',min = -90,max = 90,dv = 0,k = True)
        IK_anim.addAttr('side_to_side',at = 'double',min = -90,max = 90,dv = 0,k = True)
        IK_anim.addAttr('heel_pivot',at = 'double',min = -90,max = 90,dv = 0,k = True)
        IK_anim.addAttr('toe_pivot',at = 'double',min = -90,max = 90,dv = 0,k = True)
        IK_anim.addAttr('lean',at = 'double',min = -90,max = 90,dv = 0,k = True)
        
        #Basic Functions
        #IK_anim.balltoe_pivot >> center.rz #Balltoe Pivot
        IK_anim.heel_pivot >> back.ry #Heel Pivot
        IK_anim.toe_pivot >> front.ry #Toe Pivot
        IK_anim.lean >> front.rx #Lean
        IK_anim.toe_lift >> digit.rz #Toe Lift
        
        #Balltoe Lift
        balltoe_md = mu.create_node('multiplyDivide', n = name + '_rev_foot_balltoe_md')
        balltoe_md.input2X.set(-1)
        IK_anim.balltoe_lift >> balltoe_md.input1X
        balltoe_md.outputX >> center.rz
        
        #Side to Side
        side_range = mu.create_node('setRange',n = name + '_rev_foot_side_to_side_sr')
        rev_rot = mu.create_node('multiplyDivide',n = name + '_rev_foot_side_to_side_md')
        rev_rot_md = mu.create_node('multiplyDivide',n = name + '_rev_foot_reverse_side_to_side_md')
            
        side_range.min.set(-90,0,0)
        side_range.oldMin.set(-90,0,0)
        side_range.max.set(0,90,0)
        side_range.oldMax.set(0,90,0)
        IK_anim.side_to_side >> side_range.valueX
        IK_anim.side_to_side >> side_range.valueY
            
        side_range.outValue >> rev_rot.input1
        rev_rot.outputX >> rev_rot_md.input1X
        rev_rot.outputY >> rev_rot_md.input1Y
        rev_rot_md.input2.set(-1,-1,-1)
        rev_rot_md.outputX >> inner.rx #Inner
        rev_rot_md.outputY >> outer.rx #Outer
        
        #Heel to Toe
        heel_toe_range = mu.create_node('setRange',n = name + '_rev_foot_heel_to_toe_sr')
        heel_toe_rot = mu.create_node('multiplyDivide',n = name + '_rev_foot_heel_to_toe_md')
        heel_md = mu.create_node('multiplyDivide',n = name + '_rev_foot_heel_md')
            
        heel_toe_range.min.set(-180,0,0)
        heel_toe_range.oldMin.set(-180,0,0)
        heel_toe_range.max.set(0,180,0)
        heel_toe_range.oldMax.set(0,180,0)
        IK_anim.heel_to_toe >> heel_toe_range.valueX
        IK_anim.heel_to_toe >> heel_toe_range.valueY
            
        heel_toe_range.outValue >> heel_toe_rot.input1
        heel_toe_rot.input2.set(-1,-1,-1)
            
        heel_toe_rot.outputX >> heel_md.input1X
        heel_md.input2X.set(1)
        heel_md.outputX >> back.rotateZ #Heel
        heel_toe_rot.outputY >> front.rotateZ #Toe
    
    def IK_limb_stretch_setup(self,name,dists,IKs,IK_anim,stretch_type):
        nodes = []
        #IK Stretch Nodes
        IK_anim.addAttr('stretch',at = 'double', min = 0, max = 1, dv = 0, k = True)
        
        #Limb Stretch
        sbc = mu.create_node('blendColors',n = name + '_stretch_bc')
        gsmd = mu.create_node('multiplyDivide',n = name + '_global_scale_md')
        smd = mu.create_node('multiplyDivide',n = name + '_stretch_md')
        cond = mu.create_node('condition',n = name + '_stretch_condition')
        pv_b = mu.create_node('blendColors', n = name + '_PV_bc')
        dis = dists[0]
        
        gsmd.input2X.set(mu.get_bone_length(IKs[0],IKs[2]))
        self.node.global_scale >> gsmd.input1X
        
        smd.operation.set(2)
        dis.distance >> smd.input1X
        gsmd.outputX >> smd.input2X
    
        smd.outputX >> sbc.color1R
        sbc.color2.set(1,1,1)
        IK_anim.stretch >> sbc.blender
        
        dis.distance >> cond.firstTerm
        gsmd.outputX >> cond.secondTerm
        smd.outputX >> cond.colorIfTrueR
        cond.outColorR >> sbc.color1R
        cond.operation.set(3)
        
        if stretch_type == 'position':
            for i, ik in enumerate(IKs[:-1]):
                md = mu.create_node('multiplyDivide',n = IKs[i + 1] + '_stretch')
                md.input1X.set(IKs[i + 1].tx.get())
                sbc.outputR >> md.input2X
                md.outputX >> IKs[i + 1].tx
                nodes.append(md)
        else:
            for i, ik in enumerate(IKs[:-1]):
                md = mu.create_node('multiplyDivide',n = ik + '_stretch')
                md.input1X.set(1)
                sbc.outputR >> md.input2X
                md.outputX >> ik.sx
                nodes.append(md)
        return nodes
    
    def pole_vector_stretch(self,IKs,PV_anim,IK_mds,dists,stretch_type):
        sbcs = []
        PV_anim.addAttr('pole_vector_lock',at = 'double', min = 0, max = 1, dv = 0, k = True)
        for i, d in enumerate(dists):
            ob, ik = pm.listConnections(IK_mds[i].outputX)

            md = mu.create_node('multiplyDivide',n = d.replace('distShape','md'))
            if stretch_type == 'position': 
                if IKs[i+1].tx.get() < 0: md.input2X.set(-1)
                else: md.input2X.set(1)
            else: md.input2X.set(mu.get_bone_length(IKs[i],IKs[i+1]))
            d.distance >> md.input1X
            
            eq = mu.create_node('multiplyDivide',n = d.replace('distShape','_normalize_md'))
            eq.operation.set(2)
            md.outputX >> eq.input1X
            self.node.global_scale >> eq.input2X
            
            sbc = mu.create_node('blendColors',n = d.replace('distShape','bc'))
            eq.outputX >> sbc.color1R
            IK_mds[i].outputX >> sbc.color2R
            
            PV_anim.pole_vector_lock >> sbc.blender
            sbc.outputR >> ob.color1R
            if stretch_type == 'position': sbc.outputR >> ik.translateX
            else: sbc.outputR >> ik.scaleX
            sbcs += [sbc]
        
        return sbcs
        
    def PV_FK_setup(self,name,IKH,IK_anim,PV_anim,IKs,locs,blends,end = False):
        if not isinstance(IKs,list): IKs = [IKs]
        if not isinstance(locs,list): locs = [locs]
        FK_anims, FK_nulls = mu.create_anims(IKs, name, suffix = 'PV_FK_anim', end = end)
        rev = mu.create_node('reverse',n = PV_anim.replace('PV_anim','PV_FK_rev'))
        if self.__class__.__name__ in ['FKIKArm','FKIKBendyArm']: constraint_objs = locs + [IKH] + [IKs[1]]
        else: constraint_objs = locs + IKH
        
        PV_anim.addAttr('FK_mode',at = 'double',min = 0,max = 1,dv = 0,k = True)
        PV_anim.FK_mode >> FK_nulls[1].visibility
        PV_anim.FK_mode >> rev.inputX
        rev.outputX >> IK_anim.getParent().visibility
        
        for i, x in enumerate(constraint_objs):
            if self.__class__.__name__ in ['FKIKArm','FKIKBendyArm']:
                if x != IKs[1]: con = pm.parentConstraint(FK_anims[1],x,mo = True,w = 0)
                else: con = pm.orientConstraint(FK_anims[1],x,mo = True,w = 0)
                FK_anims[-1].visibility.set(1)
            else: 
                if i > 1: con = pm.parentConstraint(FK_anims[i],x,mo = True,w = 0)
                else: con = pm.parentConstraint(FK_anims[1],x,mo = True,w = 0)
            ats = pm.listAttr(con,st = ['*W0','*W1'])
            rev.outputX >> con.attr(ats[0])
            PV_anim.FK_mode >> con.attr(ats[1])
            
        mu.aligner(FK_nulls[0],PV_anim)
        pm.parent(FK_nulls[1],PV_anim)
        pm.delete(FK_nulls[0])
        
        new_blend = mu.create_node('blendColors',n = name + '_PV_mode_blend')
        PV_anim.FK_mode >> new_blend.blender
        new_blend.color1R.set(1)
        PV_anim.pole_vector_lock >> new_blend.color2R
        for bl in blends: new_blend.outputR >> bl.blender
        
        return FK_anims[1:]
        
    def IK_pivot_setup(self,name,bones,IK_anim,pivots):
        pns = ['back','inner','outer','front','center','end','digit','digit_end']
        new_pivots = []
        roll_null = pm.group(n = '{0}_IK_roll_grp'.format(name),em = True)
        mu.aligner(roll_null,pivots[0])
        IK_anim.addAttr('roll_anim_vis',at = 'double',min = 0,max = 1,dv = 0,k = True)
        IK_anim.roll_anim_vis >> roll_null.visibility
        
        anims,new_pivots = mu.create_anims(pivots[:-2],name,suffix = 'roll_anim')
        digits,digit_pivots = mu.create_anims(pivots[-2:],name + '_digit',suffix = 'roll_anim')
        pm.parent(new_pivots[0],roll_null)
        pm.parent(digit_pivots[0],anims[3])
        anims += digits
        new_pivots += digit_pivots
        pm.makeIdentity(new_pivots[0],a = True, t = True, r = True, s=True, jo = False)
        mu.lock_and_hide_attrs(anims,['translate','scale','radius','visibility'])
        mu.lock_and_hide_attrs(new_pivots,['translate','scale','radius','visibility'])
        
        for i, anim in enumerate(anims):
            new_pivots[i].rename('{0}_{1}_pivot_null'.format(name,pns[i]))
            anim.rename('{0}_{1}_pivot_anim'.format(name,pns[i]))
            if pivots[i] not in bones: pm.delete(pivots[i])
            if pns[i] in ['inner','outer']:
                mu.lock_and_hide_attrs(anim,['rotateY','rotateZ'])
                mu.lock_and_hide_attrs(new_pivots[i],['rotateY','rotateZ'])
            
        pm.parent(roll_null,IK_anim)
        return new_pivots, anims, roll_null
    
    def set_distance_nodes(self, name,IKH, IKs, IK_anim, PV):
        pm.select(cl = True)
        constraints = []
        limb_dist = pm.distanceDimension(sp=(0,1000,0),ep=(0,1000,1)).getParent().rename(name + '_dist')
        upper_pv_dist = pm.distanceDimension(sp=(1,1000,0),ep=(1,1000,1)).getParent().rename(name + '_upper_pv_dist')
        lower_pv_dist = pm.distanceDimension(sp=(1,1000,1),ep=(1,1000,2)).getParent().rename(name + '_lower_pv_dist')
        lower_dist = pm.distanceDimension(sp=(1,1000,2),ep=(1,1000,3)).getParent().rename(name + '_lower_dist')
        upper_dist = pm.distanceDimension(sp=(1,1000,3),ep=(1,1000,4)).getParent().rename(name + '_upper_dist')
        
        loc1 = pm.PyNode('locator1').rename(name + '_upper_pv_loc')
        loc2 = pm.PyNode('locator2').rename(name + '_lower_pv_loc')
        loc3 = pm.PyNode('locator3').rename(IKs[0].replace('IK_joint','loc'))
        loc4 = pm.PyNode('locator4').rename(IKs[1].replace('IK_joint','loc'))
        loc5 = pm.PyNode('locator5').rename(IKs[2].replace('IK_joint','loc'))
        loc6 = pm.PyNode('locator6').rename(name + '_middle_loc')
        loc7 = pm.PyNode('locator7').rename(name + '_upper_loc')
        
        locs = [loc1,loc2,loc3,loc4,loc5,loc6,loc7]
        dists = [limb_dist,upper_pv_dist,lower_pv_dist,upper_dist,lower_dist]
        conTo = [IKs[0],IK_anim,IKs[0],PV,IK_anim,IKs[1],IKs[0]]
        
        #Locator Positions
        for i in range(0,7):
            mu.aligner(locs[i],conTo[i])
            if conTo[i] != IKs[0]: constraints.append(pm.parentConstraint(conTo[i],locs[i],mo = False))
        
        for i, dist in enumerate(dists):
            if i == 0 or i > 2: val = dist.distance.get()
            else: val = IKs[i].tx.get()
            dist.addAttr('default',at = 'double',dv = val)
            dist.default.lock()

        return [locs, [x.getShape() for x in dists], constraints]
    
    def setup_soft_IK(self, name, bones, IK_anim, PV_anim, dist, pos,area = None, stretch = False):
        #Variables
        IK_anim.addAttr('soft_IK',at = 'double',min = 0,max = 1, dv = 0, k = True)
        length = mu.get_bone_length(bones[0],bones[2])

        #Soft IK Setup
        pm.select(cl = True)
        soft_start = pm.joint(n=(name + '_soft_IK_joint'),p=(0,0,0))
        soft_end = pm.joint(n=(name + '_soft_IK_end_joint'),p=(0,0,0))
        soft_end.translate.set(1,0,0)
        mu.aligner(soft_start,bones[0],rotation = False)
        soft_IKH, eff = pm.ikHandle(n=(name + '_soft_IK'),sol='ikSCsolver',sj=soft_start,ee=soft_end,ccv=False,pcv=False)
        softs = [soft_start,soft_IKH]
        if area == None: pm.parentConstraint(IK_anim, soft_IKH, mo = False)
        else: pm.parentConstraint(area, soft_IKH, mo = False)
        
        #Setup
        mu.con_link([soft_start,soft_end],self.node,'soft_IK_joints')
        mu.con_link(soft_IKH,self.node,'IK_handles')
        
        #di
        di = mu.create_node('multiplyDivide',n = name + '_soft_IK_di')
        di.operation.set(2)
        dist.distance >> di.input1X
        self.node.global_scale >> di.input2X
        
        #D
        D = mu.create_node('multiplyDivide',name + '_soft_IK_D')
        D.input1X.set(length)
        D.input2X.set(1)
        
        #Ds = D - soft_IK
        Ds= pm.shadingNode('plusMinusAverage',au=True)
        Ds.operation.set(2)
        D.outputX >> Ds.input1D[0]
        IK_anim.soft_IK >> Ds.input1D[1]
        
        #(di - Ds)
        di_minus_Ds= pm.shadingNode('plusMinusAverage',au=True)
        di_minus_Ds.operation.set(2)
        di.outputX >> di_minus_Ds.input1D[0]
        Ds.output1D >> di_minus_Ds.input1D[1]
        
        #-(di - Ds)
        neg_di_Ds = mu.create_node('multiplyDivide',n = name + 'soft_IK_negative_md')
        di_minus_Ds.output1D >> neg_di_Ds.input1X
        neg_di_Ds.input2X.set(-1)
        
        #exp(-(di-Ds))
        exp = mu.create_node('multiplyDivide',n = name + '_soft_IK_exp_md')
        exp.operation.set(3)
        exp.input1X.set(2.7182)
        neg_di_Ds.outputX >> exp.input2X
        
        #1 - exp(-(di-Ds))
        one = mu.create_node('multiplyDivide',n = name + 'soft_IK_one_md')
        one.input1X.set(1)
        one.input2X.set(1)
        one_minus_exp = pm.shadingNode('plusMinusAverage',au=True)
        one_minus_exp.operation.set(2)
        one.outputX >> one_minus_exp.input1D[0]
        exp.outputX >> one_minus_exp.input1D[1]
        
        #soft(1 - exp(-(di-Ds)))
        soft_times = mu.create_node('multiplyDivide',n = name + '_soft_IK_md')
        one_minus_exp.output1D >> soft_times.input1X
        IK_anim.soft_IK >> soft_times.input2X
        
        Ds_minus_everything = pm.shadingNode('plusMinusAverage',au=True)
        Ds_minus_everything.operation.set(1)
        Ds.output1D >> Ds_minus_everything.input1D[0]
        soft_times.outputX >> Ds_minus_everything.input1D[1]
        
        #if di > Ds
        cond = mu.create_node('condition',n = name + '_soft_IK_condition')
        cond.operation.set(2)
        Ds_minus_everything.output1D >> cond.colorIfTrueR
        di.outputX >> cond.colorIfFalseR
        di.outputX >> cond.firstTerm
        Ds.output1D >> cond.secondTerm
        
        #Constraint Setup
        if stretch == False: pm.delete(pm.listRelatives(pos, type = pm.nt.Constraint, c = True)[0])
        con = pm.parentConstraint(soft_end, pos, mo = False)
        if stretch == True: 
            ats = pm.listAttr(con,st=['*W0','*W1'])
            bl = mu.create_node('blendColors',n = name + '_soft_IK_blend')
            rev = mu.create_node('reverse',n = name + '_soft_IK_rev')
            PV_anim.pole_vector_lock >> bl.color2R
            PV_anim.FK_mode >> bl.blender
            bl.outputR >> rev.inputX
            rev.outputX >> con.attr(ats[1])
            bl.outputR >> con.attr(ats[0])
            
        #Stretch Setup
        if stretch == True:
            times_stretch = mu.create_node('multiplyDivide',n = name + '_soft_IK_stretch_md')
            cond.outColorR >> times_stretch.input1X
            pm.PyNode(name + '_stretch_bc').outputR >> times_stretch.input2X #sbc from setup_stretch_mode()
            times_stretch.outputX >> soft_end.tx
        else: cond.outColorR >> soft_end.tx
        
        return [soft_start,soft_end], soft_IKH
    
    def setup_stretch_mode(self):
        #IK Stretch Nodes
        name = self.node.side.get() + '_' + self.node.limb.get()
        bones = pm.listConnections(self.node.bones)
        IKs = pm.listConnections(self.node.IK_joints)
        locs, dists = self.set_distance_nodes()
        IK_anim, PV_anim = pm.listConnections(self.node.IK_anims)
        IK_anim.addAttr('stretch',at = 'double', min = 0, max = 1, dv = 0, k = True)
        IK_anim.addAttr('pole_vector_lock',at = 'double', min = 0, max = 1, dv = 0, k = True)
        
        #Limb Stretch
        sbc = mu.create_node('blendColors',n = name + '_stretch_bc')
        gsmd = mu.create_node('multiplyDivide',n = name + '_global_scale_md')
        smd = mu.create_node('multiplyDivide',n = name + '_stretch_md')
        cond = mu.create_node('condition',n = name + '_stretch_condition')
        pv_b = mu.create_node('blendColors', n = name + '_PV_bc')
        dis = dists[0].getShape()
        
        gsmd.input2X.set(mu.get_bone_length(bones[0],bones[2]))
        self.node.global_scale >> gsmd.input1X
        
        smd.operation.set(2)
        dis.distance >> smd.input1X
        gsmd.outputX >> smd.input2X
    
        smd.outputX >> sbc.color1R
        sbc.color2.set(1,1,1)
        IK_anim.stretch >> sbc.blender
        
        dis.distance >> cond.firstTerm
        gsmd.outputX >> cond.secondTerm
        smd.outputX >> cond.colorIfTrueR
        cond.outColorR >> sbc.color1R
        cond.operation.set(3)
        
        for i, ik in enumerate(IKs[:-1]): sbc.outputR >> ik.scaleX

    def FK_to_IK_switch(self):
        switch = pm.listConnections(self.node.switch)[0]
        IK_snaps = pm.listConnections(self.node.IK_snaps)
        IK_anims = pm.listConnections(self.node.IK_anims)
        FKs = pm.listConnections(self.node.FK_anims)[:2]
        node_type = self.node.node_type.get()
        for IK in IK_anims: mu.set_to_default_pose(IK)
        
        #Function
        if self.node.stretch.get() == True:
            if node_type not in ['FKIKSplineChain','FKIKRibbonChain']:
                if self.node.stretch.get() == True:
                    IK_anims[1].stretch.set(1)
                    IK_anims[0].FK_mode.set(0)
                    if round(FKs[0].stretch.get(),3) != 1 or round(FKs[1].stretch.get(),3) != 1:
                        IK_anims[0].pole_vector_lock.set(1)
        
        if node_type in ['FKIKBipedLeg','FKIKBipedLeg','FKIKQuadLeg']:
            toe_FK = pm.listConnections(self.node.FK_anims)[-1]
            IK_anims[1].toe_lift.set(toe_FK.rz.get())
                
        for i, IK in enumerate(IK_anims): mu.aligner(IK,IK_snaps[i])
        switch.FKIK_switch.set(1)
        
    def IK_to_FK_switch(self):
        switch = pm.listConnections(self.node.switch)[0]
        FK_anims = pm.listConnections(self.node.FK_anims)
        IK_joints = pm.listConnections(self.node.IK_joints)
        node_type = self.node.node_type.get()
        
        if self.node.stretch.get() == True:
            if node_type in ['FKIKSplineChain','FKIKRibbonChain']: dists = pm.listConnections(self.node.distances)
            else: dists = pm.listConnections(self.node.distances)[-2:]
            
            for i, dist in enumerate(dists):
                if self.node.stretch_type.get() == 'scale': st_val = IK_joints[i].sx.get()
                else: st_val = (dist.distance.get() / dist.default.get()) / self.node.global_scale.get()
                if FK_anims[i].hasAttr('stretch'): FK_anims[i].stretch.set(st_val)
                
        #Function
        for i, FK in enumerate(FK_anims): mu.aligner(FK,IK_joints[i])
        switch.FKIK_switch.set(0)

    def FKIK_group_vis_setup(self,switch,FK_grp,IK_grp):
        switch_at = pm.listAttr(switch,k = True)[0]
        switch.attr(switch_at) >> IK_grp.visibility
        rev = mu.create_node('reverse',n = FK_grp + '_vis_rev')
        switch.attr(switch_at) >> rev.inputX
        rev.outputX >> FK_grp.visibility
        
    def FKIK_constraint_setup(self, bones,controls,FK_anims,IKs,stretch_type):
        constraints = []
        if stretch_type == 'scale':
            con = pm.pointConstraint(FK_anims[0], controls[0],mo = True)
            pm.pointConstraint(IKs[0], controls[0], mo = True)
            pm.pointConstraint(controls[0],bones[0])
            constraints.append(con)
        for i, anim in enumerate(FK_anims):
            if stretch_type == 'scale':
                con = pm.orientConstraint(anim, controls[i], mo = False, w = 1)
                pm.orientConstraint(IKs[i], controls[i], mo = True, w = 0)
                controls[i].rotate >> bones[i].rotate
                controls[i].scale >> bones[i].scale
            else: 
                con = pm.parentConstraint(anim, controls[i], mo = False, w = 1)
                pm.parentConstraint(IKs[i], controls[i], mo = True, w = 0)
                con.interpType.set(2)
                pm.parentConstraint(controls[i],bones[i],mo = False)
            constraints.append(con)
        return constraints
        
    def IK_anim_snaps(self, FK_anims, IK_anims, IK_anim_num, stretch):
        IK_snaps = []
        snap_nulls = []
        node_type = self.node.node_type.get()
        numbers = [0,(len(FK_anims)-1)]
        integer = float(len(FK_anims))/ float(IK_anim_num - 1)
        for i in range(1, (IK_anim_num - 1)): numbers.insert(i,int(round(integer * i) - 1))
        areas = [FK_anims[x] for x in numbers]
    
        for i, a in enumerate(areas):
            pm.select(cl = True)
            snap_null = pm.group(n = IK_anims[i] + '_snap_null',em = True)
            snap = pm.group(n = IK_anims[i] + '_snap',em = True)
            pm.parent(snap,snap_null)
            IK_snaps.append(snap)
            snap_nulls.append(snap_null)
            
            if node_type in ['FKIKSplineChain','FKIKRibbonChain']:
                pm.parent(snap_null, a)
                mu.aligner([snap_null,snap], IK_anims[i])
                if stretch == True and snap.tx.get() > 0.0001:
                    md = mu.create_node('multiplyDivide',n = snap + '_md')
                    md.input1X.set(snap.tx.get())
                    a.stretch >> md.input2X
                    md.outputX >> snap.translateX
            else:
                mu.aligner([snap_null,snap],a)
                pm.parent(snap_null,a)
                pm.parentConstraint(a, snap, mo = True)
        
        mu.lock_and_hide_attrs(snap_nulls,'all')
        mu.con_link(IK_snaps,self.node,'IK_snaps')
        return IK_snaps
        
    #================================================================================================#
    def skin_curves(self,bones,nurb_curve):
        start, end = bones
        cvs = pm.ls(nurb_curve.cv[:],fl = True)
        skin = pm.skinCluster(bones,nurb_curve,n = nurb_curve + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
        inf = [[1.00,0.00],[1.00,0.00],[0.75,0.25],[0.50,0.50],[0.25,0.75],[0.00,1.00],[0.00,1.00]]
        for i, cv in enumerate(cvs): pm.skinPercent(skin,cv,tv = [(start,inf[i][0]),(end,inf[i][1])])
    
    def bendy_setup(self):
        #Variables
        name = self.node.side.get() + '_' + self.node.limb.get()
        hidden_grp = pm.listConnections(self.node.hidden_grp)[0]
        anim_grp = pm.listConnections(self.node.anim_grp)[0]
        bones = pm.listConnections(self.node.bones)
        controls = pm.listConnections(self.node.control_joints)
        rolls = {'upper': pm.listConnections(self.node.upper_rolls), 'lower': pm.listConnections(self.node.lower_rolls)}
        if 'Leg' in self.__class__.__name__: bones, controls = bones[:3], controls[:3]
        all_rolls     =      []
        blends        =      []
        bendy_anims  =      []
        all_nulls     =      []
        roll_controls =      []
        skin_nurbs    =      []
        normal_nurbs  =      []
        blend_nurbs   =      []
        dir = ['upper','lower']
        
        null_rots = mu.duplicate_chain(controls,name,'rot_null')
        skin_jnt_grp = pm.group(n = name + '_bendy_skin_jnt_grp',em = True)
        curve_dist_grp = pm.group(n = name + '_curve_dist_grp',em = True)
        curve_dist_grp.inheritsTransform.set(0)
        pm.parent(curve_dist_grp,hidden_grp)
        twist_md = mu.create_node('multiplyDivide',n = name + '_twist_md')
        twist_md.input2.set(1,-1,-1)
        if self.node.side.get() == 'left': twist_md.input2.set(-1,1,1)
        
        for i, d in enumerate(dir):
            segment = [bones[i],bones[i + 1]]
            reverse = False
            if d == 'upper': reverse = True
            twists = mu.duplicate_chain(segment,name + '_' + d,'twist_joint',reverse = reverse)
            twist_null = mu.stack_chain(twists[0],'joint','null')[0]
            new_controls = mu.duplicate_chain(rolls[d],name + '_' + d,'control_joint')
            normal_skin_jnts = mu.duplicate_chain(segment,name + '_' + d,'normal_skin_joint')
            pm.parentConstraint(segment[0],normal_skin_jnts[0],mo = True)
            pm.pointConstraint(segment[1],normal_skin_jnts[1],mo = True)
            normal_skin_jnts[-1].jointOrient.set(0,0,0)
            twists[-1].jointOrient.set(0,0,0)
            
            #Curves and Anims
            pm.parent(normal_skin_jnts[0],skin_jnt_grp)
            all_rolls += rolls[d]
            roll_controls += new_controls
            anims, nulls, nurb = mu.create_spline_anims(name + '_' + d + '_bendy','bendy_anim',rolls[d],spans = 4)
            normal_nurb = pm.duplicate(nurb)[0].rename(nurb.replace('bendy','normal'))
            final_nurb = pm.duplicate(nurb)[0].rename(nurb.replace('_bendy',''))
            blends += pm.blendShape(nurb,normal_nurb,final_nurb,n = name + '_' + d + '_blend')
            pm.parent(nulls,null_rots[i])
            bendy_anims += anims
            all_nulls    += nulls
            skin_nurbs   += [nurb]
            normal_nurbs += [normal_nurb]
            blend_nurbs  += [final_nurb]
            
            #Finalize Segment
            self.skin_curves(normal_skin_jnts,normal_nurb)
            IKH, eff = pm.ikHandle(n = name + '_' + d + '_IKH',sj = new_controls[0], ee = new_controls[-1], sol = 'ikSplineSolver', ccv = False, c = final_nurb)
            pm.parent(IKH,hidden_grp)
            pm.parent(new_controls[0],controls[i])
            mds, locs, dists = self.IK_spline_stretch_setup(new_controls, final_nurb, 'position')
            pm.parent(locs, [dist.getParent() for dist in dists], curve_dist_grp)
            [new_controls[j].translate >> r.translate for j, r in enumerate(rolls[d])]
            [new_controls[j].rotate >> r.rotate for j, r in enumerate(rolls[d])]
            
            #Twist Setup
            pm.parent(twist_null,controls[i])
            t_IKH, eff = pm.ikHandle(n = name + '_' + d + '_twist_IKH',sj = twists[0], ee = twists[-1], sol = 'ikSCsolver')
            pm.parent(t_IKH,hidden_grp)
            if d == 'upper':
                twists[0].rx >> twist_md.input1X
                twists[0].rx >> twist_md.input1Y
                twist_md.outputX >> IKH.twist
                twist_md.outputY >> IKH.roll
            else:
                pm.parentConstraint(controls[i + 1],t_IKH, mo = True)
                twists[0].rx >> twist_md.input1Z
                twist_md.outputZ >> IKH.twist

        #Anim and Nurb Setup
        pm.delete(bendy_anims[2],all_nulls[2])
        del(bendy_anims[2],all_nulls[2])
        rots = mu.stack_chain(bendy_anims,rep = 'anim',wi = 'rot')
        skin_joints = mu.duplicate_chain(bendy_anims,name,'skin_joint',separate = True)
        [x.rename('{0}_{1}_bendy_anim'.format(name,i + 1)) for i, x in enumerate(bendy_anims)]
        [x.rename('{0}_{1}_bendy_null'.format(name,i + 1)) for i, x in enumerate(all_nulls)]
        [controls[i + 1].translate >> x.translate for i, x in enumerate(null_rots[1:])]
        [controls[i + 1].rotate >> x.rotate for i, x in enumerate(null_rots[1:])]
        pm.parentConstraint(controls[0],null_rots[0],mo = True)
        [x.drawStyle.set(2) for x in null_rots]
        pm.parent(skin_joints,skin_jnt_grp)
        pm.parent(skin_jnt_grp,hidden_grp)
        pm.skinCluster(skin_joints[:3],skin_nurbs[0],n = skin_nurbs[0] + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
        pm.skinCluster(skin_joints[2:],skin_nurbs[1],n = skin_nurbs[1] + '_skin',tsb = True, mi = 2, sm = 1, nw = 1)
        
        #Middle Bend
        mid_rot = rots[2]
        md = mu.create_node('multiplyDivide',name + '_half_rotation_md')
        null_rots[1].rotate >> md.input1
        md.input2.set(-2,-2,-2)
        md.operation.set(2)
        md.output >> mid_rot.rotate
        
        #Constraint Setup
        [pm.parentConstraint(x,skin_joints[i],mo = True) for i, x in enumerate(bendy_anims)]
        pm.pointConstraint(bendy_anims[0],bendy_anims[2],all_nulls[1],mo = True)
        pm.pointConstraint(bendy_anims[2],bendy_anims[-1],all_nulls[3],mo = True)
        pm.pointConstraint(null_rots[-1],all_nulls[-1],mo = True)
        
        #Blend Anim
        blend_anim, blend_null = mu.create_anims(bones[2], name, suffix = 'blend_anim', r = 3,end = False)
        pm.parentConstraint(bones[2],blend_null,mo = True)
        blend_anim.addAttr('bendy_mode',at = 'double',min = 0,max = 1,dv = 0,k = True)
        rev = mu.create_node('reverse',n = name + '_bendy_blend_rev')
        blend_anim.bendy_mode >> rev.inputX
        [blend_anim.bendy_mode >> blends[i].attr(sn) for i, sn in enumerate(skin_nurbs)]
        [rev.outputX >> blends[i].attr(nn) for i, nn in enumerate(normal_nurbs)]
        
        #Nurb Grp Setup
        nurb_grp = pm.group(n = 'nurb_grp',em = True)
        nurb_grp.inheritsTransform.set(0)
        pm.parent(nurb_grp,hidden_grp)
        pm.parent(skin_nurbs,normal_nurbs,blend_nurbs,nurb_grp)
        
        #Anim Grp Setup
        bendy_anim_grp = pm.group(n = 'bendy_anims_grp',em = True)
        pm.parent(bendy_anim_grp,blend_null,anim_grp)
        pm.parent(null_rots[0],bendy_anim_grp)
        blend_anim.bendy_mode >> bendy_anim_grp.visibility
        
        #Lock and Hide Attributes
        mu.lock_and_hide_attrs(blend_anim,['translate','rotate','scale','v','radius'])
        mu.lock_and_hide_attrs(bendy_anims,['scale','v','radius'])
        mu.lock_and_hide_attrs([bendy_anims[0],bendy_anims[-1]],['translate'])
        
        #Finalize
        mu.con_link(bendy_anims,self.node,'bendy_anims')
        mu.con_link(bendy_anims + [blend_anim],self.node,'anims')
        
        '''pm.aimConstraint(anims[0],all_nulls[1],aim = (1,0,0),wut = 'vector',u = (0,1,0),wu = (0,0,1), mo = True)
        pm.aimConstraint(anims[2],all_nulls[3],aim = (1,0,0),wut = 'vector',u = (0,1,0),wu = (0,0,1), mo = True)
        pm.aimConstraint(anims[1],all_nulls[0],aim = (1,0,0),wut = 'vector',u = (0,1,0),wu = (0,0,1), mo = True)
        pm.aimConstraint(anims[2],all_nulls[-1],aim = (1,0,0),wut = 'vector',u = (0,1,0),wu = (0,0,1), mo = True)'''