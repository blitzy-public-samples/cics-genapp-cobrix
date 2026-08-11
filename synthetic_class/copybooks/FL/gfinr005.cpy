******************************************************************
*  COPYBOOK  : GFINR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : IN
******************************************************************
 01  RT-FIN-RATING.

          03 RT-FIN-TERRITORY-CODE            PIC X(3).
          03 RT-FIN-CLASS-CODE                PIC X(4).
          03 RT-FIN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FIN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FIN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FIN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FIN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FIN-RATED-PREMIUM             PIC 9(9)V9(2).
