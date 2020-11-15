Grid Models
============================

.. autoclass:: models.grid_model.AbstractGrid
   :members: new, shape, colors, reset, _tighten, gravitize, is_hidden, adjacent

.. autoclass:: models.grid_model.MoveGrid
   :show-inheritance:
   :members: new, reorient, finalize

.. autoclass:: models.grid_model.BoardGrid
   :show-inheritance:
   :members: apply_move, revert_move, revert

.. autoclass:: models.grid_model.HoverGrid
   :show-inheritance:
   :members: new, fit_move, assign_move
             
.. autoclass:: models.grid_model.Move
