******************************************************************
*  COPYBOOK  : GONHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NH
******************************************************************
 01  RT-ONH-RATING.

          03 RT-ONH-TERRITORY-CODE            PIC X(3).
          03 RT-ONH-CLASS-CODE                PIC X(4).
          03 RT-ONH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONH-RATED-PREMIUM             PIC 9(9)V9(2).
