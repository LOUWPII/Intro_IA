%estado(posicion robot, posicion caja, encima de la caja, tiene la bateria)t
%accion(estado inicial, movimiento, estado final)

bateria(8).
limite(10).
inicial(estado(1,5,no,no)).

costo(mover_derecha,1).
costo(mover_izquierda,1).
costo(empujar_derecha,2).
costo(empujar_izquierda,2).
costo(subir_caja,1).
costo(agarrar_bateria,1).

%Mover derecha 
accion(
  estado(PosRobot, PosCaja, no, TieneBateria),
          mover_derecha,
          estado(NuevaPosRobot, PosCaja, no, TieneBateria)
          ) :-
    		limite(Limite),
    		PosRobot < Limite,
    		NuevaPosRobot is PosRobot + 1.

%Mover izquierda
accion(
  estado(PosRobot, PosCaja, no, TieneBateria),
          mover_izquierda,
          estado(NuevaPosRobot, PosCaja, no, TieneBateria)
          ) :-
    		PosRobot > 1,
    		NuevaPosRobot is PosRobot - 1.

%Empujar derecha
accion(
  estado(PosRobot, PosCaja, no, TieneBateria),
          empujar_derecha,
          estado(NuevaPosRobot, NuevaPosCaja, no, TieneBateria)
          ) :-
    		limite(Limite),
    		PosRobot < Limite,
			PosRobot =:= PosCaja,
    		NuevaPosRobot is PosRobot + 1,
			NuevaPosCaja is PosCaja + 1.

%Empujar izquierda
accion(
  estado(PosRobot, PosCaja, no, TieneBateria),
          empujar_izquierda,
          estado(NuevaPosRobot, NuevaPosCaja, no, TieneBateria)
          ) :-
    		PosRobot > 1,
			PosRobot =:= PosCaja,
    		NuevaPosRobot is PosRobot - 1,
			NuevaPosCaja is PosCaja - 1.

%Subir a la Caja
accion(
  estado(PosRobot, PosCaja, no, TieneBateria),
          subir_caja,
          estado(PosRobot, PosCaja, si, TieneBateria)
          ) :-
            PosRobot =:= PosCaja.

%Agarrar Bateria
accion(
  estado(PosRobot, PosCaja, si, no),
          agarrar_bateria,
          estado(PosRobot, PosCaja, si, si)
          ) :-
    		bateria(PosBateria),
    		PosRobot =:= PosCaja,
    		PosCaja =:= PosBateria.

heuristica(estado(_, _, _, si), 0) :- !.

heuristica(estado(Robot,Caja,si,no),1) :-
    bateria(Bateria),
    Robot =:= Caja,
    Caja =:= Bateria, !.

heuristica(estado(Robot, Caja, Encima, no), H) :-
    bateria(B),
    DistCajaBateria is abs(Caja - B),
    DistRobotCaja is abs(Robot - Caja),
    (Encima == si -> Penalizacion = 0 ; Penalizacion = 1),
    (Robot =:= Caja -> JuntoCaja = 1 ; JuntoCaja = 0),
    H is DistCajaBateria + DistRobotCaja + Penalizacion + 1 - JuntoCaja.
