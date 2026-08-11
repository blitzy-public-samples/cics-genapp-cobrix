******************************************************************
*  COPYBOOK  : GFWIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : WI
******************************************************************
 01  RT-FWI-RATING.

          03 RT-FWI-TERRITORY-CODE            PIC X(3).
          03 RT-FWI-CLASS-CODE                PIC X(4).
          03 RT-FWI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FWI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FWI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FWI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FWI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FWI-RATED-PREMIUM             PIC 9(9)V9(2).
