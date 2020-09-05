
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ASSIGNMENT LBRACE RBRACE VAR WHITESPACEexpression : VAR LBRACE expression RBRACEexpression : variable_expression\n                  | variable_expression expressionvariable_expression : VAR ASSIGNMENT'
    
_lr_action_items = {'VAR':([0,3,4,5,],[2,2,2,-4,]),'$end':([1,3,5,6,8,],[0,-2,-4,-3,-1,]),'LBRACE':([2,],[4,]),'ASSIGNMENT':([2,],[5,]),'RBRACE':([3,5,6,7,8,],[-2,-4,-3,8,-1,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,3,4,],[1,6,7,]),'variable_expression':([0,3,4,],[3,3,3,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> VAR LBRACE expression RBRACE','expression',4,'p_expression_expr','parser.py',13),
  ('expression -> variable_expression','expression',1,'p_expression_variable_expansion','parser.py',18),
  ('expression -> variable_expression expression','expression',2,'p_expression_variable_expansion','parser.py',19),
  ('variable_expression -> VAR ASSIGNMENT','variable_expression',2,'p_expression_equal','parser.py',32),
]
