******************************************************************
*  COPYBOOK  : GOOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : OH
******************************************************************
 01  RT-OOH-RATING.

          03 RT-OOH-TERRITORY-CODE            PIC X(3).
          03 RT-OOH-CLASS-CODE                PIC X(4).
          03 RT-OOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OOH-RATED-PREMIUM             PIC 9(9)V9(2).
