******************************************************************
*  COPYBOOK  : GONMR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : NM
******************************************************************
 01  RT-ONM-RATING.

          03 RT-ONM-TERRITORY-CODE            PIC X(3).
          03 RT-ONM-CLASS-CODE                PIC X(4).
          03 RT-ONM-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ONM-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ONM-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ONM-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ONM-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ONM-RATED-PREMIUM             PIC 9(9)V9(2).
